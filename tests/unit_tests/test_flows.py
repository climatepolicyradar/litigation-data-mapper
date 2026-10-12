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


@patch("litigation_data_mapper.flows.time.sleep", Mock())
@patch("litigation_data_mapper.flows.get_ssm_parameter", Mock())
@patch("litigation_data_mapper.flows.boto3.client")
def test_await_bulk_import_waits_for_the_result(mock_client):
    list_objects = mock_client.return_value.list_objects_v2
    list_objects.side_effect = [{}, {}, {"Contents": [{"Key": "uuid-result-x.json"}]}]

    await_bulk_import.fn("uuid")

    assert list_objects.call_count == 3


@patch("litigation_data_mapper.flows.get_ssm_parameter", Mock())
@patch("litigation_data_mapper.flows.boto3.client")
def test_await_bulk_import_raises_when_the_import_fails(mock_client):
    mock_client.return_value.list_objects_v2.return_value = {
        "Contents": [{"Key": "uuid-failure-x.json"}]
    }

    with pytest.raises(RuntimeError):
        await_bulk_import.fn("uuid")
