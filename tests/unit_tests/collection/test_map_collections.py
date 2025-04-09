from datetime import datetime
from typing import Any
from unittest.mock import patch

import pytest

from litigation_data_mapper.datatypes import Failure, LitigationContext
from litigation_data_mapper.parsers.collection import (
    map_collections,
    process_collection_data,
)


@pytest.fixture
def parsed_collection_data():
    return [
        {
            "import_id": "Sabin.collection.1.0",
            "description": "Challenge to the determination that designation of critical habitat for the endangered loch ness would not be prudent.",
            "title": "Center for Biological Diversity v. Wildlife Service",
            "metadata": {"id": ["1"]},
        },
        {
            "import_id": "Sabin.collection.2.0",
            "description": "Challenge to to project approvals issued by Department of Environmental Protection.",
            "title": "Matter of project approvals approved by DOE",
            "metadata": {"id": ["2"]},
        },
    ]


def test_returns_expected_collection_data_structure(
    mock_collection_data: list[dict[str, Any]],
    parsed_collection_data: list[dict[str, Any]],
    mock_context: LitigationContext,
):
    with patch(
        "litigation_data_mapper.parsers.collection.LAST_IMPORT_DATE",
        new=datetime.strptime("2024-12-01T12:00:00", "%Y-%m-%dT%H:%M:%S"),
    ):
        collection_data = map_collections(mock_collection_data, mock_context)
        assert collection_data is not None
        assert collection_data != []

        assert len(collection_data) == len(mock_collection_data)
        assert collection_data == parsed_collection_data


def test_generates_collection_import_id(mock_collection_data: list[dict[str, Any]]):
    bundle_one = mock_collection_data[0]
    bundle_one["id"] = 789

    mapped_collection_data = process_collection_data(bundle_one, 0, 789)
    assert not isinstance(mapped_collection_data, Failure)
    assert mapped_collection_data["import_id"] == "Sabin.collection.789.0"


def tests_map_collections_strips_html_characters_from_title(mock_collection_data):
    bundle_one = mock_collection_data[0]
    bundle_one["title"][
        "rendered"
    ] = "Center for Biological Diversity v. Wildlife Service &amp; Others"

    mapped_collection_data = process_collection_data(bundle_one, 0, 1)
    assert not isinstance(mapped_collection_data, Failure)
    assert (
        mapped_collection_data["title"]
        == "Center for Biological Diversity v. Wildlife Service & Others"
    )


def test_raises_error_on_validating_collections_for_missing_keys(
    mock_context: LitigationContext,
):
    collection_data = [
        {
            "id": 1,
            "date": "2021-01-01T00:00:00",
            "title": {
                "rendered": "Center for Biological Diversity v. Wildlife Service"
            },
            "slug": "center-biological-diversity-v-wildlife-service",
        }
    ]

    with pytest.raises(AttributeError) as e:
        map_collections(collection_data, mock_context)

    assert (
        str(e.value)
        == "Required fields ['ccl_core_object', 'modified_gmt'] not present in data: ['date', 'id', 'rendered', 'slug', 'title']"
    )


def test_skips_collection_data_item_if_missing_title_information(
    mock_context: LitigationContext,
):
    id = 1
    collection_data = [
        {
            "id": id,
            "date": "2021-01-01T00:00:00",
            "modified_gmt": "2025-01-01T17:00:00",
            "title": {},
            "slug": "center-biological-diversity-v-wildlife-service",
            "acf": {
                "ccl_core_object": "Challenge to the determination that designation of critical habitat for the endangered loch ness would not be prudent."
            },
        }
    ]

    with patch(
        "litigation_data_mapper.parsers.collection.LAST_IMPORT_DATE",
        new=datetime.strptime("2024-12-01T12:00:00", "%Y-%m-%dT%H:%M:%S"),
    ):
        mapped_collection_data = map_collections(collection_data, mock_context)
        assert mapped_collection_data == []

        assert len(mock_context.failures) == 1
        assert mock_context.failures[0] == Failure(
            id=id, type="case_bundle", reason="Does not contain a title"
        )


def test_skips_collection_data_item_if_missing_description_information(
    mock_context: LitigationContext,
):
    id = 1
    collection_data = [
        {
            "id": id,
            "date": "2021-01-01T00:00:00",
            "modified_gmt": "2025-01-01T17:00:00",
            "title": {
                "rendered": "Center for biological diversity versus wildlife service"
            },
            "slug": "center-biological-diversity-v-wildlife-service",
            "acf": {"ccl_core_object": ""},
        }
    ]
    with patch(
        "litigation_data_mapper.parsers.collection.LAST_IMPORT_DATE",
        new=datetime.strptime("2024-12-01T12:00:00", "%Y-%m-%dT%H:%M:%S"),
    ):
        mapped_collection_data = map_collections(collection_data, mock_context)
        assert mapped_collection_data == []

        assert len(mock_context.failures) == 1
        assert mock_context.failures[0] == Failure(
            id=id, type="case_bundle", reason="Does not contain a description"
        )


def test_skips_collection_data_item_if_missing_bundle_id(
    mock_context: LitigationContext,
):
    collection_data = [
        {
            "id": None,
            "date": "2021-01-01T00:00:00",
            "modified_gmt": "2025-01-01T17:00:00",
            "title": {
                "rendered": "Center for Biological Diversity v. Wildlife Service"
            },
            "slug": "center-biological-diversity-v-wildlife-service",
            "acf": {
                "ccl_core_object": "Challenge to the determination that designation of critical habitat for the endangered loch ness would not be prudent."
            },
        },
        {
            "id": 2,
            "date": "2021-01-01T00:00:00",
            "modified_gmt": "2025-01-01T17:00:00",
            "title": {
                "rendered": "Center for Biological Diversity v. Wildlife Service 2"
            },
            "slug": "center-biological-diversity-v-wildlife-service-second",
            "acf": {
                "ccl_core_object": "Second Challenge to the determination that designation of critical habitat for the endangered loch ness would not be prudent."
            },
        },
    ]

    assert len(mock_context.failures) == 0

    with patch(
        "litigation_data_mapper.parsers.collection.LAST_IMPORT_DATE",
        new=datetime.strptime("2024-12-01T12:00:00", "%Y-%m-%dT%H:%M:%S"),
    ):
        mapped_collection_data = map_collections(collection_data, mock_context)
        assert len(mapped_collection_data) == 1
        assert len(mock_context.failures) == 1

        assert mock_context.failures[0] == Failure(
            id=None,
            type="case_bundle",
            reason="Does not contain a bundle id at index (0)",
        )
