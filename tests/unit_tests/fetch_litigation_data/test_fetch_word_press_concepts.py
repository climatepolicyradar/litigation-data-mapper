from unittest.mock import MagicMock, patch

import pytest

from litigation_data_mapper.wordpress import (
    IncompleteWordPressFetchError,
    fetch_word_press_concepts,
)

ENDPOINT = "https://example.com/wp-json/wp/v2/jurisdiction"


def mock_response(ids: list[int], total: int) -> MagicMock:
    response = MagicMock()
    response.__enter__.return_value = response
    response.json.return_value = [{"id": i, "name": f"concept {i}"} for i in ids]
    response.headers = {"X-WP-Total": str(total)}
    return response


@patch("litigation_data_mapper.wordpress.create_retry_session")
def test_fetches_every_concept_by_excluding_concepts_already_seen_so_there_are_no_duplicates(
    mock_session,
):
    get = mock_session.return_value.get
    get.side_effect = [
        mock_response([1, 2], total=3),
        mock_response([2, 3], total=3),
        mock_response([], total=3),
    ]

    result = fetch_word_press_concepts(ENDPOINT)

    assert [c["id"] for c in result] == [1, 2, 3]


@patch("litigation_data_mapper.wordpress.create_retry_session")
def test_raises_if_fewer_concepts_than_wordpress_reports(mock_session):
    mock_session.return_value.get.side_effect = [
        mock_response([1], total=2),
        mock_response([], total=2),
    ]

    with pytest.raises(
        IncompleteWordPressFetchError,
        match=f"Fetched 1 concepts from {ENDPOINT} but WordPress reports 2",
    ):
        fetch_word_press_concepts(ENDPOINT)


@patch("litigation_data_mapper.wordpress.create_retry_session")
def test_raises_if_exclude_is_ignored(mock_session):
    mock_session.return_value.get.side_effect = [
        mock_response([1, 2], total=4),
        mock_response([1, 2], total=4),
    ]

    with pytest.raises(IncompleteWordPressFetchError, match="exclude"):
        fetch_word_press_concepts(ENDPOINT)
