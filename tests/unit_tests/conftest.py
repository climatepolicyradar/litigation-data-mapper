import os
from typing import Generator
from unittest.mock import MagicMock, patch

import boto3
import pytest
from moto import mock_aws
from mypy_boto3_s3 import S3Client
from prefect import Flow, State


@pytest.fixture
def mock_prefect_slack_webhook():
    """Patch the SlackWebhook class to return a mock object."""
    with patch("litigation_data_mapper.utils.SlackWebhook") as mock_SlackWebhook:
        mock_prefect_slack_block = MagicMock()
        mock_SlackWebhook.load.return_value = mock_prefect_slack_block
        yield mock_SlackWebhook, mock_prefect_slack_block


@pytest.fixture
def mock_flow():
    """Mock Prefect flow object."""
    mock_flow = MagicMock(spec=Flow)
    mock_flow.name = "TestFlow"
    yield mock_flow


@pytest.fixture
def mock_flow_run():
    """Mock Prefect flow run object."""
    mock_flow_run = MagicMock()
    mock_flow_run.name = "TestFlowRun"
    mock_flow_run.id = "test-flow-run-id"
    mock_flow_run.state = MagicMock(spec=State)
    mock_flow_run.state.name = "Completed"
    mock_flow_run.state.message = "message"
    mock_flow_run.state.timestamp = "2025-01-28T12:00:00+00:00"

    yield mock_flow_run


@pytest.fixture(scope="function")
def mock_aws_creds():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
    os.environ["AWS_SECURITY_TOKEN"] = "test"
    os.environ["AWS_SESSION_TOKEN"] = "test"


@pytest.fixture
def mock_s3_client() -> Generator[S3Client, None, None]:
    with mock_aws():
        yield boto3.client("s3", region_name="eu-west-1")
