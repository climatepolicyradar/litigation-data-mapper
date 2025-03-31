from unittest.mock import MagicMock, patch

import requests

from litigation_data_mapper.fetch_litigation_data import (
    ENDPOINTS,
    LitigationType,
    fetch_litigation_data,
    fetch_word_press_data,
)
from litigation_data_mapper.wordpress import create_retry_session


def test_create_retry_session():
    with patch("litigation_data_mapper.wordpress.requests.Session") as mock_session:
        session = create_retry_session()
        assert session is not None
        mock_session.assert_called_once()


def test_fetch_word_press_data_success():
    with patch("litigation_data_mapper.wordpress.requests.Session") as mock_session:
        mock_response = MagicMock()
        mock_response.json.return_value = [{"id": 1, "title": "Test Case"}]
        mock_response.headers = {"X-WP-TotalPages": "1"}
        mock_response.raise_for_status = MagicMock()

        mock_session.return_value.get.return_value = mock_response

        data = fetch_word_press_data(ENDPOINTS["case_bundles"])
        assert data is not None
        assert len(data) == 1
        assert data[0]["title"] == "Test Case"


def test_fetch_word_press_data_failure():
    with patch("litigation_data_mapper.wordpress.requests.Session") as mock_session:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("Error")

        mock_session.return_value.get.return_value = mock_response

        data = fetch_word_press_data(ENDPOINTS["case_bundles"])
        assert data == []


@patch("litigation_data_mapper.fetch_litigation_data.extract_concepts")
@patch("litigation_data_mapper.fetch_litigation_data.fetch_word_press_data")
def test_fetch_litigation_data(mock_extract_concepts, mock_fetch_word_press_data):

    mock_return_value = [{"key": "value"}]
    mock_fetch_word_press_data.return_value = mock_return_value
    mock_extract_concepts.return_value = mock_return_value

    result = fetch_litigation_data()

    expected_result: LitigationType = {
        "collections": mock_return_value,
        "families": {
            "us_cases": mock_return_value,
            "global_cases": mock_return_value,
            "jurisdictions": mock_return_value,
        },
        "documents": mock_return_value,
        "concepts": mock_return_value,  # type: ignore
    }
    assert result == expected_result
