from litigation_data_mapper.cli import wrangle_data
from litigation_data_mapper.fetch_litigation_data import LitigationType


def test_successfully_maps_litigation_data_to_the_required_schema():
    litigation_data: LitigationType = {
        "collections": [
            {
                "id": 1,
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
                                "ccl_nonus_document_type": "judgement",
                                "ccl_nonus_filing_date": "20230718",
                                "ccl_nonus_file": 2,
                                "ccl_nonus_document_summary": "",
                            },
                            {
                                "ccl_nonus_document_type": "judgement",
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
    }

    expected_mapped_data = {
        "collections": [
            {
                "import_id": "Litigation.collection.1.0",
                "description": "Test core object",
                "title": "Test US case bundle title",
                "metadata": {"id": ["1"]},
            }
        ],
        "families": [
            {
                "category": "Litigation",
                "collections": ["Litigation.collection.1.0"],
                "geographies": ["USA", "US-NY"],
                "import_id": "Litigation.family.1.0",
                "metadata": {
                    "case_number": ["1:20-cv-12345"],
                    "core_object": [],
                    "id": ["1"],
                    "original_case_name": [],
                    "status": ["Test US case outcome"],
                },
                "summary": "Test core object",
                "title": "Test US case title",
            },
            {
                "category": "Litigation",
                "collections": [],
                "geographies": ["CAN", "USA"],
                "import_id": "Litigation.family.2.0",
                "metadata": {
                    "case_number": ["1:20-cv-12345"],
                    "core_object": ["Test global case core object"],
                    "id": ["2"],
                    "original_case_name": ["Test global case name"],
                    "status": ["Pending"],
                },
                "summary": "Test global case summary",
                "title": "Test global case title",
            },
        ],
        "documents": [
            {
                "family_import_id": "Litigation.family.2.0",
                "import_id": "Litigation.document.2.n0000",
                "metadata": {"id": ["2"]},
                "source_url": "https://adaptation/case-document.pdf",
                "title": "Test global case title - judgement",
                "variant_name": "Original Language",
            },
            {
                "family_import_id": "Litigation.family.2.0",
                "import_id": "Litigation.document.2.n0001",
                "metadata": {"id": ["3"]},
                "source_url": "https://lawsuit/case-document.pdf",
                "title": "Test global case title - judgement",
                "variant_name": "Original Language",
            },
            {
                "family_import_id": "Litigation.family.1.0",
                "import_id": "Litigation.document.1.n0000",
                "metadata": {"id": ["1"]},
                "source_url": "https://energy/case-document.pdf",
                "title": "Test US case headline",
                "variant_name": "Original Language",
            },
        ],
        "events": [
            {
                "import_id": "Litigation.event.1.n0000",
                "family_import_id": "Litigation.family.1.0",
                "family_document_import_id": "",
                "event_type_value": "Filing Year for Action",
                "title": "Filing Year for Action",
                "date": "20250101",
                "metadata": {
                    "event_type": ["Filing Year for Action"],
                    "description": ["Filing Year for Action"],
                    "datetime_event_name": ["Filing Year for Action"],
                },
            },
            {
                "import_id": "Litigation.event.1.n0001",
                "family_import_id": "Litigation.family.1.0",
                "family_document_import_id": "Litigation.document.1.n0000",
                "event_type_value": "petition",
                "title": "petition",
                "date": "20250122",
                "metadata": {
                    "event_type": ["petition"],
                    "description": ["Test US case summary"],
                    "datetime_event_name": ["Filing Year for Action"],
                },
            },
            {
                "import_id": "Litigation.event.2.n0000",
                "family_import_id": "Litigation.family.2.0",
                "family_document_import_id": "",
                "event_type_value": "Filing Year for Action",
                "title": "Filing Year for Action",
                "date": "20220101",
                "metadata": {
                    "event_type": ["Filing Year for Action"],
                    "description": ["Filing Year for Action"],
                    "datetime_event_name": ["Filing Year for Action"],
                },
            },
            {
                "import_id": "Litigation.event.2.n0001",
                "family_import_id": "Litigation.family.2.0",
                "family_document_import_id": "Litigation.document.2.n0000",
                "event_type_value": "judgement",
                "title": "judgement",
                "date": "20230718",
                "metadata": {
                    "event_type": ["judgement"],
                    "description": [""],
                    "datetime_event_name": ["Filing Year for Action"],
                },
            },
            {
                "import_id": "Litigation.event.2.n0002",
                "family_import_id": "Litigation.family.2.0",
                "family_document_import_id": "Litigation.document.2.n0001",
                "event_type_value": "judgement",
                "title": "judgement",
                "date": "20240704",
                "metadata": {
                    "event_type": ["judgement"],
                    "description": ["Test summary"],
                    "datetime_event_name": ["Filing Year for Action"],
                },
            },
        ],
    }

    assert wrangle_data(litigation_data) == expected_mapped_data
