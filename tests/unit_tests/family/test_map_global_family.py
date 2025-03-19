from unittest.mock import patch

import pytest

from litigation_data_mapper.parsers.family import map_families, process_global_case_data


@pytest.fixture()
def mapped_global_family():
    return {
        "category": "Litigation",
        "collections": [],
        "geographies": [
            "CAN",
        ],
        "import_id": "Litigation.family.1.0",
        "metadata": {
            "case_number": [
                "1:20-cv-12345",
            ],
            "core_object": [
                "Challenge to the determination that designation of critical "
                "habitat for the endangered loch ness would not be prudent.",
            ],
            "id": [
                "1",
            ],
            "original_case_name": [
                "Center for Biological Diversity v. Wildlife Service",
            ],
            "status": [
                "Pending",
            ],
        },
        "summary": "Summary of the challenge to the determination that designation of "
        "critical habitat for the endangered loch ness would not be prudent.",
        "title": "Center for Biological Diversity v. Wildlife Service",
    }


def test_maps_jurisdictions_to_global_family(mock_family_data: dict, mock_context):
    with patch(
        "litigation_data_mapper.parsers.helpers.map_global_jurisdictions"
    ) as mapped_jurisdictions:
        mapped_jurisdictions.return_value = {
            2: {"name": "Canada", "iso": "CAN", "parent": 0},
            3: {"name": "United Kingdom", "iso": "GBR", "parent": 0},
            4: {"name": "Australia", "iso": "AUS", "parent": 0},
        }

    mock_family_data["global_cases"][0]["jurisdiction"] = [2, 3, 4]

    family_data = map_families(mock_family_data, mock_context)
    assert family_data is not None
    global_family = family_data[1]

    assert global_family != {}
    assert global_family is not None
    assert global_family["geographies"] == ["CAN", "GBR", "AUS"]


def test_maps_jurisdictions_as_default_international_iso_code_if_case_jurisdiction_not_found(
    mock_family_data: dict, mock_context: dict
):
    with patch(
        "litigation_data_mapper.parsers.helpers.map_global_jurisdictions"
    ) as mapped_jurisdictions:
        mapped_jurisdictions.return_value = {
            2: {"name": "Canada", "iso": "CAN", "parent": 0},
            3: {"name": "United Kingdom", "iso": "GBR", "parent": 0},
            4: {"name": "Australia", "iso": "AUS", "parent": 0},
        }

    mock_family_data["global_cases"][0]["jurisdiction"] = [47]
    family_data = map_families(mock_family_data, mock_context)
    assert family_data is not None
    global_family = family_data[1]

    assert global_family != {}
    assert global_family is not None
    assert global_family["geographies"] == ["XAA"]


def test_skips_processing_global_case_data_if_family_contains_missing_data(
    capsys, mock_global_case: dict
):
    mock_global_case["acf"]["ccl_nonus_summary"] = ""
    case_id = mock_global_case.get("id", 2)
    geographies = ["JAM"]

    process_global_case_data(mock_global_case, geographies, case_id)

    captured = capsys.readouterr()
    assert "🛑 Skipping global case (1), missing: summary" in captured.out.strip()


@pytest.mark.parametrize(
    (
        "missing_data_key",
        "expected_return",
        "error_message",
    ),
    [
        (
            "ccl_nonus_status",
            None,
            "🛑 Skipping global case (1), missing family metadata: status",
        ),
        (
            "ccl_nonus_case_name",
            None,
            "🛑 Skipping global case (1), missing family metadata: original_case_name",
        ),
        (
            "ccl_nonus_core_object",
            None,
            "🛑 Skipping global case (1), missing family metadata: core_object",
        ),
        (
            "ccl_nonus_reporter_info",
            None,
            "🛑 Skipping global case (1), missing family metadata: reporter_info",
        ),
    ],
)
def test_skips_process_global_case_data_if_family_metadata_contains_missing_data(
    missing_data_key: str,
    expected_return,
    error_message: str,
    capsys,
    mock_global_case: dict,
):
    mock_global_case["acf"][missing_data_key] = ""
    case_id = mock_global_case.get("id", 2)
    geographies = ["JAM"]

    mapped_global_family = process_global_case_data(
        mock_global_case, geographies, case_id
    )
    assert expected_return == mapped_global_family

    captured = capsys.readouterr()
    assert error_message in captured.out.strip()


def test_maps_global_case(mock_global_case: dict, mapped_global_family: dict):
    case_id = mock_global_case.get("id", 2)
    geographies = ["CAN"]

    mapped_family = process_global_case_data(mock_global_case, geographies, case_id)

    assert mapped_family is not None
    assert mapped_family == mapped_global_family


def test_generates_family_import_id(mock_global_case: dict):
    case_id = 34
    mock_global_case["id"] = case_id
    geographies = ["CAN"]

    mapped_family = process_global_case_data(mock_global_case, geographies, case_id)

    assert mapped_family is not None
    assert mapped_family != {}
    assert mapped_family["import_id"] == f"Litigation.family.{case_id}.0"
