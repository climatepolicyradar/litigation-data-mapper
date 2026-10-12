from contextlib import nullcontext
from unittest.mock import Mock, patch

import pytest
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


@pytest.mark.parametrize(
    "outcome, expectation",
    [("result", nullcontext()), ("failure", pytest.raises(RuntimeError))],
)
@patch("litigation_data_mapper.flows.get_ssm_parameter", Mock(return_value="bucket"))
def test_await_bulk_import(mock_s3_client, outcome, expectation):
    mock_s3_client.create_bucket(
        Bucket="bucket",
        CreateBucketConfiguration={"LocationConstraint": "eu-west-1"},
    )
    mock_s3_client.put_object(Bucket="bucket", Key=f"uuid-{outcome}-corpus.json")

    with expectation:
        await_bulk_import.fn("uuid")
