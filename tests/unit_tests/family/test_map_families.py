from datetime import datetime
from unittest.mock import patch

import pytest

from litigation_data_mapper.datatypes import Failure
from litigation_data_mapper.parsers.family import map_families


@pytest.fixture
def parsed_family_data():
    return [
        {
            "category": "Litigation",
            "collections": [
                "Sabin.collection.1.0",
                "Sabin.collection.2.0",
            ],
            "concepts": [],
            "geographies": [
                "USA",
                "US-TX",
            ],
            "import_id": "Sabin.family.1.0",
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
            "summary": "The description of cases relating to litigation of the Sierra Club",
            "title": "Sierra Club v. New York State Department of Environmental "
            "Conservation",
        },
        {
            "category": "Litigation",
            "collections": [],
            "concepts": [],
            "geographies": [
                "CAN",
            ],
            "import_id": "Sabin.family.2.0",
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


def test_skips_mapping_families_if_data_missing_jurisdictions(capsys, mock_context):
    family_data = {
        "us_cases": [
            {"id": 1, "title": "Center for Biological Diversity v. Wildlife Service"},
        ],
        "global_cases": [
            {"id": 2, "title": "Center for Biological Diversity v. Wildlife Service 2"},
        ],
        "jurisdictions": [],
    }

    mapped_families = map_families(family_data, context=mock_context, concepts={})
    assert len(mapped_families) == 0

    captured = capsys.readouterr()
    assert (
        "No jurisdictions provided in the data. Skipping family litigation."
        in captured.out.strip()
    )


def test_skips_mapping_families_if_data_missing_us_cases(capsys, mock_context):
    family_data = {
        "us_cases": [],
        "global_cases": [
            {"id": 2, "title": "Center for Biological Diversity v. Wildlife Service 2"},
        ],
        "jurisdictions": [{"id": 1, "name": "United States", "parent": 0}],
    }

    mapped_families = map_families(family_data, context=mock_context, concepts={})
    assert len(mapped_families) == 0

    captured = capsys.readouterr()
    assert (
        "🛑 No US cases found in the data. Skipping family litigation."
        in captured.out.strip()
    )


def test_skips_mapping_families_if_data_missing_global_cases(capsys, mock_context):
    family_data = {
        "us_cases": [
            {"id": 1, "title": "Center for Biological Diversity v. Wildlife Service"}
        ],
        "global_cases": [],
        "jurisdictions": [{"id": 1, "name": "United States", "parent": 0}],
    }

    mapped_families = map_families(family_data, context=mock_context, concepts={})
    assert len(mapped_families) == 0

    captured = capsys.readouterr()
    assert (
        "🛑 No global cases found in the data. Skipping family litigation."
        in captured.out.strip()
    )


def test_maps_families(mock_family_data, parsed_family_data, mock_context):
    with patch(
        "litigation_data_mapper.parsers.collection.LAST_IMPORT_DATE",
        new=datetime.strptime("2024-12-01T12:00:00", "%Y-%m-%dT%H:%M:%S"),
    ):
        family_data = map_families(mock_family_data, context=mock_context, concepts={})
        assert family_data is not None
        assert len(family_data) == 2

        assert family_data == parsed_family_data


def test_maps_families_handles_no_original_case_name_for_global_cases(mock_context):
    with patch(
        "litigation_data_mapper.parsers.helpers.map_global_jurisdictions"
    ) as mapped_jurisdictions:
        mapped_jurisdictions.return_value = {
            2: {"name": "Canada", "iso": "CAN", "parent": 0},
        }

    test_family_data = {
        "us_cases": [{}],
        "global_cases": [
            {
                "id": 1,
                "modified_gmt": "2025-04-01T12:00:00",
                "title": {
                    "rendered": "Center for Biological Diversity v. Wildlife Service"
                },
                "jurisdiction": [1],
                "acf": {
                    "ccl_nonus_case_name": None,
                    "ccl_nonus_summary": "Summary of the challenge to the determination that designation of critical habitat for the endangered loch ness would not be prudent.",
                    "ccl_nonus_reporter_info": "1:20-cv-12345",
                    "ccl_nonus_status": "Pending",
                    "ccl_nonus_core_object": "Challenge to the determination that designation of critical habitat for the endangered loch ness would not be prudent.",
                    "ccl_nonus_case_country": "US",
                    "ccl_nonus_case_documents": [
                        {
                            "ccl_nonus_document_type": "judgment",
                            "ccl_nonus_filing_date": "20230718",
                            "ccl_nonus_file": 89750,
                            "ccl_nonus_document_summary": "",
                        },
                    ],
                },
            }
        ],
        "jurisdictions": [
            {"id": 1, "name": "Australia", "parent": 0},
        ],
    }

    expected_family_data = [
        {
            "category": "Litigation",
            "collections": [],
            "concepts": [],
            "geographies": [
                "AUS",
            ],
            "import_id": "Sabin.family.1.0",
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
                "original_case_name": [],
                "status": [
                    "Pending",
                ],
            },
            "summary": "Summary of the challenge to the determination that designation of "
            "critical habitat for the endangered loch ness would not be prudent.",
            "title": "Center for Biological Diversity v. Wildlife Service",
        }
    ]

    with patch(
        "litigation_data_mapper.parsers.family.LAST_IMPORT_DATE",
        new=datetime.strptime("2025-02-01T12:00:00", "%Y-%m-%dT%H:%M:%S"),
    ):
        family_data = map_families(test_family_data, mock_context, concepts={})

    assert family_data == expected_family_data


def test_skips_mapping_families_with_missing_modified_date(mock_context):
    test_family_data = {
        "us_cases": [{"id": 1}],
        "global_cases": [{"id": 2}],
        "jurisdictions": [{"id": 1, "name": "United States", "parent": 0}],
    }

    family_data = map_families(test_family_data, context=mock_context, concepts={})

    assert not family_data
    assert [1, 2] == mock_context.skipped_families
    assert [
        Failure(id=1, type="case", reason="Does not contain a modified_gmt timestamp."),
        Failure(id=2, type="case", reason="Does not contain a modified_gmt timestamp."),
    ] == mock_context.failures
