from unittest.mock import MagicMock, patch

import requests

from litigation_data_mapper.fetch_litigation_data import (
    ENDPOINTS,
    create_retry_session,
    fetch_litigation_data,
    fetch_word_press_data,
)


def test_create_retry_session():
    with patch(
        "litigation_data_mapper.fetch_litigation_data.requests.Session"
    ) as mock_session:
        session = create_retry_session()
        assert session is not None
        mock_session.assert_called_once()


def test_fetch_word_press_data_success():
    with patch(
        "litigation_data_mapper.fetch_litigation_data.requests.Session"
    ) as mock_session:
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
    with patch(
        "litigation_data_mapper.fetch_litigation_data.requests.Session"
    ) as mock_session:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("Error")

        mock_session.return_value.get.return_value = mock_response

        data = fetch_word_press_data(ENDPOINTS["case_bundles"])
        assert data == []


def test_fetch_litigation_data():
    with patch(
        "litigation_data_mapper.fetch_litigation_data.fetch_word_press_data"
    ) as mock_fetch:
        mock_fetch.return_value = [{"id": 1, "title": "Test Case"}]

        data = fetch_litigation_data()
        assert "collections" in data
        assert len(data["collections"]) == 1
        assert data["collections"][0]["title"] == "Test Case"
