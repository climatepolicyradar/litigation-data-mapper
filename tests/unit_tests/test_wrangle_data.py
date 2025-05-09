import pytest
from freezegun import freeze_time

from litigation_data_mapper.cli import wrangle_data


@pytest.fixture()
def mock_litigation_data():
    yield {
        "collections": [
            {
                "id": 1,
                "modified_gmt": "2025-02-01T12:00:00",
                "type": "case_bundle",
                "title": {"rendered": "Test US case bundle title"},
                "acf": {
                    "ccl_cases": [1],
                    "ccl_core_object": "Test core object",
                    "ccl_case_categories": [],
                    "ccl_principal_law": [],
                },
            }
        ],
        "families": {
            "us_cases": [
                {
                    "id": 1,
                    "modified_gmt": "2025-02-01T12:00:00",
                    "title": {"rendered": "Test US case title"},
                    "type": "case",
                    "entity": [],
                    "acf": {
                        "ccl_case_bundle": [1],
                        "ccl_docket_number": "1:20-cv-12345",
                        "ccl_entity": 245,
                        "ccl_filing_year_for_action": "2025",
                        "ccl_state": "NY",
                        "ccl_case_documents": [
                            {
                                "ccl_document_type": "petition",
                                "ccl_filing_date": "20250122",
                                "ccl_file": 1,
                                "ccl_document_headline": "Test US case headline",
                                "ccl_document_summary": "Test US case summary",
                                "ccl_outcome": "Test US case outcome",
                            },
                        ],
                    },
                }
            ],
            "global_cases": [
                {
                    "id": 2,
                    "modified_gmt": "2025-02-01T12:00:00",
                    "title": {"rendered": "Test global case title"},
                    "type": "non_us_case",
                    "jurisdiction": [1, 2],
                    "acf": {
                        "ccl_nonus_case_name": "Test global case name",
                        "ccl_nonus_summary": "Test global case summary",
                        "ccl_nonus_reporter_info": "1:20-cv-12345",
                        "ccl_nonus_filing_year_for_action": "2022",
                        "ccl_nonus_status": "Pending",
                        "ccl_nonus_core_object": "Test global case core object",
                        "ccl_nonus_case_country": "US",
                        "ccl_nonus_case_documents": [
                            {
                                "ccl_nonus_document_type": "judgment",
                                "ccl_nonus_filing_date": "20230718",
                                "ccl_nonus_file": 2,
                                "ccl_nonus_document_summary": "",
                            },
                            {
                                "ccl_nonus_document_type": "judgment",
                                "ccl_nonus_filing_date": "20240704",
                                "ccl_nonus_file": 3,
                                "ccl_nonus_document_summary": "Test summary",
                            },
                        ],
                    },
                }
            ],
            "jurisdictions": [
                {"id": 1, "name": "United States", "parent": 0},
                {"id": 2, "name": "Canada", "parent": 0},
            ],
        },
        "documents": [
            {"id": 1, "source_url": "https://energy/case-document.pdf"},
            {"id": 2, "source_url": "https://adaptation/case-document.pdf"},
            {"id": 3, "source_url": "https://lawsuit/case-document.pdf"},
        ],
        "concepts": {},
    }


@pytest.fixture()
def expected_mapped_data():
    yield {
        "collections": [
            {
                "import_id": "Sabin.collection.1.0",
                "description": "Test core object",
                "title": "Test US case bundle title",
                "metadata": {"id": ["1"]},
            }
        ],
        "families": [
            {
                "category": "Litigation",
                "collections": ["Sabin.collection.1.0"],
                "concepts": [],
                "geographies": ["USA", "US-NY"],
                "import_id": "Sabin.family.1.0",
                "metadata": {
                    "case_number": ["1:20-cv-12345"],
                    "core_object": [],
                    "id": ["1"],
                    "original_case_name": [],
                    "status": ["Test US case outcome"],
                    "concept_preferred_label": [],
                },
                "summary": "Test core object",
                "title": "Test US case title",
            },
            {
                "category": "Litigation",
                "collections": [],
                "concepts": [],
                "geographies": ["CAN", "USA"],
                "import_id": "Sabin.family.2.0",
                "metadata": {
                    "case_number": ["1:20-cv-12345"],
                    "core_object": ["Test global case core object"],
                    "id": ["2"],
                    "original_case_name": ["Test global case name"],
                    "status": ["Pending"],
                    "concept_preferred_label": [],
                },
                "summary": "Test global case summary",
                "title": "Test global case title",
            },
        ],
        "documents": [
            {
                "family_import_id": "Sabin.family.2.0",
                "import_id": "Sabin.document.2.2",
                "metadata": {"id": ["2"]},
                "source_url": "https://adaptation/case-document.pdf",
                "title": "Test global case title - judgment",
                "variant_name": "Original Language",
            },
            {
                "family_import_id": "Sabin.family.2.0",
                "import_id": "Sabin.document.2.3",
                "metadata": {"id": ["3"]},
                "source_url": "https://lawsuit/case-document.pdf",
                "title": "Test global case title - judgment",
                "variant_name": "Original Language",
            },
            {
                "family_import_id": "Sabin.family.1.0",
                "import_id": "Sabin.document.1.1",
                "metadata": {"id": ["1"]},
                "source_url": "https://energy/case-document.pdf",
                "title": "Test US case headline",
                "variant_name": "Original Language",
            },
        ],
        "events": [
            {
                "import_id": "Sabin.event.1.n0000",
                "family_import_id": "Sabin.family.1.0",
                "family_document_import_id": None,
                "event_type_value": "Filing Year For Action",
                "event_title": "Filing Year For Action",
                "date": "2025-01-01",
                "metadata": {
                    "event_type": ["Filing Year For Action"],
                    "description": ["Filing Year For Action"],
                    "datetime_event_name": ["Filing Year For Action"],
                },
            },
            {
                "import_id": "Sabin.event.1.n0001",
                "family_import_id": "Sabin.family.1.0",
                "family_document_import_id": "Sabin.document.1.1",
                "event_type_value": "Petition",
                "event_title": "petition",
                "date": "2025-01-22",
                "metadata": {
                    "event_type": ["Petition"],
                    "description": ["Test US case summary"],
                    "datetime_event_name": ["Filing Year For Action"],
                },
            },
            {
                "import_id": "Sabin.event.2.n0000",
                "family_import_id": "Sabin.family.2.0",
                "family_document_import_id": None,
                "event_type_value": "Filing Year For Action",
                "event_title": "Filing Year For Action",
                "date": "2022-01-01",
                "metadata": {
                    "event_type": ["Filing Year For Action"],
                    "description": ["Filing Year For Action"],
                    "datetime_event_name": ["Filing Year For Action"],
                },
            },
            {
                "import_id": "Sabin.event.2.n0001",
                "family_import_id": "Sabin.family.2.0",
                "family_document_import_id": "Sabin.document.2.2",
                "event_type_value": "Judgment",
                "event_title": "judgment",
                "date": "2023-07-18",
                "metadata": {
                    "event_type": ["Judgment"],
                    "description": [""],
                    "datetime_event_name": ["Filing Year For Action"],
                },
            },
            {
                "import_id": "Sabin.event.2.n0002",
                "family_import_id": "Sabin.family.2.0",
                "family_document_import_id": "Sabin.document.2.3",
                "event_type_value": "Judgment",
                "event_title": "judgment",
                "date": "2024-07-04",
                "metadata": {
                    "event_type": ["Judgment"],
                    "description": ["Test summary"],
                    "datetime_event_name": ["Filing Year For Action"],
                },
            },
        ],
    }


@freeze_time("2024-12-01T12:00:00")
def test_successfully_maps_litigation_data_to_the_required_schema(
    mock_litigation_data, expected_mapped_data
):
    assert (
        wrangle_data(mock_litigation_data, debug=True, get_modified_data=False)
        == expected_mapped_data
    )


@freeze_time("2025-04-01T12:00:00")
def test_skips_mapping_litigation_data_outside_of_update_window(mock_litigation_data):

    assert wrangle_data(mock_litigation_data, debug=True, get_modified_data=True) == {
        "collections": [],
        "families": [],
        "documents": [],
        "events": [],
    }


@freeze_time("2025-06-01T00:00:00")
def test_only_maps_litigation_data_that_was_modified_within_the_last_48_hrs(
    mock_litigation_data, expected_mapped_data
):
    mock_litigation_data["collections"][0]["modified_gmt"] = "2025-05-31T12:00:00"
    mock_litigation_data["collections"].append(
        {
            "id": 2,
            "modified_gmt": "2025-05-29T12:00:00",
            "type": "case_bundle",
            "title": {"rendered": "Test US case bundle title"},
            "acf": {
                "ccl_cases": [1],
                "ccl_core_object": "Test core object",
                "ccl_case_categories": [],
                "ccl_principal_law": [],
            },
        }
    )

    mock_litigation_data["families"]["us_cases"][0][
        "modified_gmt"
    ] = "2025-05-31T12:00:00"
    mock_litigation_data["families"]["global_cases"][0][
        "modified_gmt"
    ] = "2025-05-29T12:00:00"

    assert wrangle_data(mock_litigation_data, debug=True, get_modified_data=True) == {
        "collections": expected_mapped_data["collections"],
        "families": [expected_mapped_data["families"][0]],
        "documents": [expected_mapped_data["documents"][2]],
        "events": [
            expected_mapped_data["events"][0],
            expected_mapped_data["events"][1],
        ],
    }


@freeze_time("2025-04-01T12:00:00")
def test_maps_all_data_regardless_of_update_window_if_get_modified_data_flag_is_false(
    mock_litigation_data, expected_mapped_data
):
    assert (
        wrangle_data(mock_litigation_data, debug=True, get_modified_data=False)
        == expected_mapped_data
    )
