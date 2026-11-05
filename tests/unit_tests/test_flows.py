from unittest.mock import Mock, patch

import pytest
from prefect.testing.utilities import prefect_test_harness

from litigation_data_mapper.flows import await_bulk_import


@pytest.fixture(autouse=True, scope="session")
def prefect_test_fixture():
    with prefect_test_harness():
        yield


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
