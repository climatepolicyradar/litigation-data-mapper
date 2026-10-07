from unittest.mock import Mock, patch

import pytest
import requests
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


def status_response(status: str, **extra):
    """Build a stub of the admin service's bulk import status response."""
    response = Mock()
    response.raise_for_status = Mock()
    response.json = Mock(return_value={"status": status, **extra})
    return response


@patch("litigation_data_mapper.flows.time.sleep", Mock())
@patch("litigation_data_mapper.flows.get_token", Mock(return_value="test_token"))
@patch("litigation_data_mapper.flows.get_auth_config", Mock())
@patch("litigation_data_mapper.flows.requests.get")
def test_await_bulk_import_returns_when_the_import_succeeds(mock_get):
    mock_get.return_value = status_response(
        "success", duration_seconds=300, counts={"families": 1}
    )

    await_bulk_import("test-import-id")

    assert mock_get.call_count == 1


@patch("litigation_data_mapper.flows.time.sleep", Mock())
@patch("litigation_data_mapper.flows.get_token", Mock(return_value="test_token"))
@patch("litigation_data_mapper.flows.get_auth_config", Mock())
@patch("litigation_data_mapper.flows.requests.get")
def test_await_bulk_import_polls_until_the_import_finishes(mock_get):
    mock_get.side_effect = [
        status_response("running"),
        status_response("running"),
        status_response("success", duration_seconds=300, counts={"families": 1}),
    ]

    await_bulk_import("test-import-id")

    assert mock_get.call_count == 3


@patch("litigation_data_mapper.flows.time.sleep", Mock())
@patch("litigation_data_mapper.flows.get_token", Mock(return_value="test_token"))
@patch("litigation_data_mapper.flows.get_auth_config", Mock())
@patch("litigation_data_mapper.flows.requests.get")
def test_await_bulk_import_raises_when_the_import_fails(mock_get):
    mock_get.return_value = status_response("failure", error="duplicate slug")

    with pytest.raises(RuntimeError) as e:
        await_bulk_import("test-import-id")

    assert "duplicate slug" in str(e.value)


@patch("litigation_data_mapper.flows.time.sleep", Mock())
@patch("litigation_data_mapper.flows.get_token", Mock(return_value="test_token"))
@patch("litigation_data_mapper.flows.get_auth_config", Mock())
@patch("litigation_data_mapper.flows.requests.get")
def test_await_bulk_import_keeps_polling_when_the_admin_service_is_unreachable(
    mock_get,
):
    mock_get.side_effect = [
        requests.ConnectionError("admin service is being deployed"),
        status_response("success", duration_seconds=300, counts={"families": 1}),
    ]

    await_bulk_import("test-import-id")

    assert mock_get.call_count == 2


@patch("litigation_data_mapper.flows.BULK_IMPORT_TIMEOUT_SECONDS", 0)
@patch("litigation_data_mapper.flows.time.sleep", Mock())
@patch("litigation_data_mapper.flows.get_token", Mock(return_value="test_token"))
@patch("litigation_data_mapper.flows.get_auth_config", Mock())
@patch("litigation_data_mapper.flows.requests.get")
def test_await_bulk_import_raises_when_the_import_does_not_finish_in_time(mock_get):
    mock_get.return_value = status_response("running")

    with pytest.raises(TimeoutError) as e:
        await_bulk_import("test-import-id")

    assert "did not complete within" in str(e.value)
