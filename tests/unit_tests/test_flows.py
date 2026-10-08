import json
from unittest.mock import Mock, patch

import pytest
from botocore.exceptions import EndpointConnectionError
from prefect.testing.utilities import prefect_test_harness

from litigation_data_mapper.flows import await_bulk_import, sync_wordpress_to_s3
from litigation_data_mapper.wordpress_data import endpoints


@pytest.fixture(autouse=True, scope="session")
def prefect_test_fixture():
    with prefect_test_harness():
        yield


@pytest.mark.parametrize(
    "endpoint",
    endpoints,
)
@patch("litigation_data_mapper.flows.fetch_word_press_data", return_value=[1, 2, 3])
def test_sync_wordpress_to_s3(mock_fetch_word_press_data, mock_s3_client, endpoint):
    mock_s3_client.create_bucket(
        Bucket="cpr-cache",
        CreateBucketConfiguration={"LocationConstraint": "eu-west-1"},
    )

    sync_wordpress_to_s3()

    # Upload, now they should be there
    assert mock_s3_client.head_object(
        Bucket="cpr-cache", Key=f"litigation/wordpress/{endpoint}.json"
    )


BULK_IMPORT_BUCKET = "test-bulk-import-bucket"
IMPORT_ID = "test-import-id"


@pytest.fixture
def bulk_import_bucket(mock_s3_client):
    mock_s3_client.create_bucket(
        Bucket=BULK_IMPORT_BUCKET,
        CreateBucketConfiguration={"LocationConstraint": "eu-west-1"},
    )
    with patch(
        "litigation_data_mapper.flows.get_ssm_parameter",
        Mock(return_value=BULK_IMPORT_BUCKET),
    ):
        yield mock_s3_client


def write_outcome(s3_client, outcome: str, contents: dict) -> None:
    """Write an outcome file named the way the admin service names them."""
    s3_client.put_object(
        Bucket=BULK_IMPORT_BUCKET,
        Key=f"{IMPORT_ID}-{outcome}-Academic.corpus.Litigation.n0000-10-08-2026T17:00:00.json",
        Body=json.dumps(contents),
    )


@patch("litigation_data_mapper.flows.time.sleep", Mock())
def test_await_bulk_import_returns_when_the_import_succeeds(bulk_import_bucket):
    write_outcome(bulk_import_bucket, "result", {"families": ["family.1"]})

    await_bulk_import(IMPORT_ID)


@patch("litigation_data_mapper.flows.time.sleep")
def test_await_bulk_import_polls_until_the_import_finishes(
    mock_sleep, bulk_import_bucket
):
    mock_sleep.side_effect = lambda _: (
        write_outcome(bulk_import_bucket, "result", {"families": []})
        if mock_sleep.call_count == 2
        else None
    )

    await_bulk_import(IMPORT_ID)

    assert mock_sleep.call_count == 2


@patch("litigation_data_mapper.flows.time.sleep", Mock())
def test_await_bulk_import_raises_when_the_import_fails(bulk_import_bucket):
    write_outcome(bulk_import_bucket, "failure", {"error": "duplicate slug"})

    with pytest.raises(RuntimeError) as e:
        await_bulk_import(IMPORT_ID)

    assert "duplicate slug" in str(e.value)


@patch("litigation_data_mapper.flows.time.sleep", Mock())
@patch("litigation_data_mapper.flows.get_bulk_import_outcome")
def test_await_bulk_import_keeps_polling_when_s3_errors(
    mock_get_outcome, bulk_import_bucket
):
    mock_get_outcome.side_effect = [
        EndpointConnectionError(endpoint_url="https://s3"),
        ("result", {"families": []}),
    ]

    await_bulk_import(IMPORT_ID)

    assert mock_get_outcome.call_count == 2


@patch("litigation_data_mapper.flows.BULK_IMPORT_TIMEOUT_SECONDS", 0)
@patch("litigation_data_mapper.flows.time.sleep", Mock())
def test_await_bulk_import_raises_when_the_import_does_not_finish_in_time(
    bulk_import_bucket,
):
    with pytest.raises(TimeoutError) as e:
        await_bulk_import(IMPORT_ID)

    assert "did not complete within" in str(e.value)
