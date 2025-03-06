from typing import Any

import pytest

from litigation_data_mapper.parsers.collection import (
    map_collections,
    process_collection_data,
)


@pytest.fixture
def parsed_collection_data():
    return [
        {
            "import_id": "Litigation.collection.1.0",
            "description": "Challenge to the determination that designation of critical habitat for the endangered loch ness would not be prudent.",
            "title": "Center for Biological Diversity v. Wildlife Service",
            "metadata": {"id": "1"},
        },
        {
            "import_id": "Litigation.collection.2.0",
            "description": "Challenge to to project approvals issued by Department of Environmental Protection.",
            "title": "Matter of project approvals approved by DOE",
            "metadata": {"id": "2"},
        },
    ]


def test_returns_expected_collection_data_structure(
    mock_collection_data: list[dict[str, Any]],
    parsed_collection_data: list[dict[str, Any]],
):
    collection_data = map_collections(mock_collection_data, False)
    assert collection_data is not None
    assert collection_data != []

    assert len(collection_data) == len(mock_collection_data)
    assert collection_data == parsed_collection_data


def test_generates_collection_import_id(mock_collection_data: list[dict[str, Any]]):
    bundle_one = mock_collection_data[0]
    bundle_one["id"] = 789

    mapped_collection_data = process_collection_data(bundle_one, 0, "789")
    assert mapped_collection_data is not None
    assert mapped_collection_data["import_id"] == "Litigation.collection.789.0"


def tests_map_collections_strips_html_characters_from_title(mock_collection_data):
    bundle_one = mock_collection_data[0]
    bundle_one["title"][
        "rendered"
    ] = "Center for Biological Diversity v. Wildlife Service &amp; Others"

    mapped_collection_data = process_collection_data(bundle_one, 0, "1")
    assert mapped_collection_data is not None
    assert (
        mapped_collection_data["title"]
        == "Center for Biological Diversity v. Wildlife Service & Others"
    )


def test_raises_error_on_validating_collections_for_missing_keys():
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
        map_collections(collection_data, False)

    assert (
        str(e.value)
        == "Required fields ['ccl_core_object'] not present in data: ['date', 'id', 'rendered', 'slug', 'title']"
    )


def test_skips_collection_data_item_if_missing_title_information(capsys):
    collection_data = [
        {
            "id": 1,
            "date": "2021-01-01T00:00:00",
            "title": {},
            "slug": "center-biological-diversity-v-wildlife-service",
            "acf": {
                "ccl_core_object": "Challenge to the determination that designation of critical habitat for the endangered loch ness would not be prudent."
            },
        }
    ]

    mapped_collection_data = map_collections(collection_data, False)
    assert mapped_collection_data == []
    captured = capsys.readouterr()
    assert (
        "Error at bundle id : 1 - Empty values found for description and/or title. Skipping....."
        in captured.out.strip()
    )


def test_skips_collection_data_item_if_missing_bundle_id(capsys):
    collection_data = [
        {
            "id": None,
            "date": "2021-01-01T00:00:00",
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
            "title": {
                "rendered": "Center for Biological Diversity v. Wildlife Service 2"
            },
            "slug": "center-biological-diversity-v-wildlife-service-second",
            "acf": {
                "ccl_core_object": "Second Challenge to the determination that designation of critical habitat for the endangered loch ness would not be prudent."
            },
        },
    ]

    mapped_collection_data = map_collections(collection_data, False)
    assert len(mapped_collection_data) == 1

    captured = capsys.readouterr()
    assert (
        "Skipping case bundle at index: 0 as it does not contain a bundle id"
        in captured.out.strip()
    )
