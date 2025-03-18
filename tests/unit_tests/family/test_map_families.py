from unittest.mock import patch

import pytest

from litigation_data_mapper.parsers.family import map_families


@pytest.fixture
def parsed_family_data():
    return [
        {
            "category": "Litigation",
            "collections": [
                "Litigation.collection.1.0",
                "Litigation.collection.2.0",
            ],
            "geographies": [
                "USA",
                "US-TX",
            ],
            "import_id": "Litigation.family.1.0",
            "metadata": {
                "case_number": [
                    "1:20-cv-12345",
                ],
                "core_object": [],
                "id": [
                    "1",
                ],
                "original_case_name": [],
                "status": [
                    "Memorandum of law filed in support of verified petition.",
                ],
            },
            "summary": "",
            "title": "Sierra Club v. New York State Department of Environmental "
            "Conservation",
        },
        {
            "category": "Litigation",
            "collections": [],
            "geographies": [
                "CAN",
            ],
            "import_id": "Litigation.family.2.0",
            "metadata": {
                "case_number": [
                    "1:20-cv-12345",
                ],
                "core_object": [
                    "Challenge to the determination that designation of critical "
                    "habitat for the endangered loch ness would not be prudent.",
                ],
                "id": [
                    "2",
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
        },
    ]


def test_skips_mapping_families_if_data_missing_jurisdictions(capsys):
    family_data = {
        "us_cases": [
            {"id": 1, "title": "Center for Biological Diversity v. Wildlife Service"},
        ],
        "global_cases": [
            {"id": 2, "title": "Center for Biological Diversity v. Wildlife Service 2"},
        ],
        "jurisdictions": [],
    }

    context = {"debug": False, "case_bundle_ids": [1, 2]}
    mapped_families = map_families(family_data, context)
    assert len(mapped_families) == 0

    captured = capsys.readouterr()
    assert (
        "🛑 No jurisdictions provided in the family data. Skipping family litigation."
        in captured.out.strip()
    )


def test_skips_mapping_families_if_data_missing_us_cases(capsys):
    family_data = {
        "us_cases": [],
        "global_cases": [
            {"id": 2, "title": "Center for Biological Diversity v. Wildlife Service 2"},
        ],
        "jurisdictions": [{"id": 1, "name": "United States", "parent": 0}],
    }

    context = {"debug": False, "case_bundle_ids": [1, 2]}
    mapped_families = map_families(family_data, context)
    assert len(mapped_families) == 0

    captured = capsys.readouterr()
    assert (
        "🛑 No US cases found in the data. Skipping family litigation."
        in captured.out.strip()
    )


def test_skips_mapping_families_if_data_missing_global_cases(capsys):
    family_data = {
        "us_cases": [
            {"id": 1, "title": "Center for Biological Diversity v. Wildlife Service"}
        ],
        "global_cases": [],
        "jurisdictions": [{"id": 1, "name": "United States", "parent": 0}],
    }

    context = {"debug": False, "case_bundle_ids": [1, 2]}
    mapped_families = map_families(family_data, context)
    assert len(mapped_families) == 0

    captured = capsys.readouterr()
    assert (
        "🛑 No global cases found in the data. Skipping family litigation."
        in captured.out.strip()
    )


def test_maps_families(mock_family_data, parsed_family_data):
    with patch(
        "litigation_data_mapper.parsers.helpers.map_global_jurisdictions"
    ) as mapped_jurisdictions:
        mapped_jurisdictions.return_value = {
            1: {"name": "United States", "iso": "USA", "parent": 0},
            2: {"name": "Canada", "iso": "CAN", "parent": 0},
        }

    context = {"debug": False, "case_bundle_ids": [1, 2]}
    family_data = map_families(mock_family_data, context)
    assert family_data is not None
    assert len(family_data) == 2

    assert family_data == parsed_family_data
