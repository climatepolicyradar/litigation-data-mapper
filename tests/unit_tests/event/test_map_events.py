from litigation_data_mapper.parsers.event import map_events

test_litigation_data = {
    "families": {
        "us_cases": [
            {
                "id": 89975,
                "type": "case",
                "acf": {
                    "ccl_case_bundle": [8917],
                    "ccl_docket_number": "20250065 ",
                    "ccl_entity": 252,
                    "ccl_filing_year_for_action": "2019",
                    "ccl_case_documents": [
                        {
                            "ccl_document_type": "petition",
                            "ccl_filing_date": "20250227",
                            "ccl_file": 89977,
                            "ccl_document_headline": "",
                            "ccl_document_summary": "Test summary",
                            "ccl_outcome": "Test outcome",
                        }
                    ],
                },
            }
        ],
        "global_cases": [
            {
                "id": 89636,
                "type": "non_us_case",
                "acf": {
                    "ccl_nonus_reporter_info": "",
                    "ccl_nonus_filing_year_for_action": "2022",
                    "ccl_nonus_status": "Dismissed",
                    "ccl_nonus_core_object": "Complaint against company",
                    "ccl_nonus_case_documents": [
                        {
                            "ccl_nonus_document_type": "decision",
                            "ccl_nonus_filing_date": "20220914",
                            "ccl_nonus_file": 89637,
                            "ccl_nonus_document_summary": "Test summary",
                        }
                    ],
                },
            }
        ],
    }
}


expected_default_event_1 = {
    "import_id": "Litigation.event.89975.n0000",
    "family_import_id": "Litigation.family.89975.0",
    "family_document_import_id": "",
    "title": "Filing Year for Action",
    "date": "20190101",
    "metadata": {
        "event_type": ["Filing Year for Action"],
        "description": ["Filing Year for Action"],
        "datetime_event_name": ["Filing Year for Action"],
    },
}

expected_default_event_2 = {
    "import_id": "Litigation.event.89636.n0000",
    "family_import_id": "Litigation.family.89636.0",
    "family_document_import_id": "",
    "title": "Filing Year for Action",
    "date": "20220101",
    "metadata": {
        "event_type": ["Filing Year for Action"],
        "description": ["Filing Year for Action"],
        "datetime_event_name": ["Filing Year for Action"],
    },
}


def test_successfully_mapped_events_include_a_default_event_per_family():
    mapped_events = map_events(test_litigation_data, {"debug": False})
    assert expected_default_event_1 in mapped_events
    assert expected_default_event_2 in mapped_events


def test_successfully_maps_us_litigation_data_to_events():
    expected_mapped_us_event = {
        "import_id": "Litigation.event.89975.n0001",
        "family_import_id": "Litigation.family.89975.0",
        "family_document_import_id": "Litigation.document.89975.n0000",
        "title": "petition",
        "date": "20250227",
        "metadata": {
            "event_type": ["petition"],
            "description": ["Test summary"],
            "datetime_event_name": ["Filing Year for Action"],
        },
    }

    mapped_events = map_events(test_litigation_data, {"debug": False})
    assert expected_default_event_1 in mapped_events
    assert expected_mapped_us_event in mapped_events


def test_successfully_maps_global_litigation_data_to_events():
    expected_mapped_global_event = {
        "import_id": "Litigation.event.89636.n0001",
        "family_import_id": "Litigation.family.89636.0",
        "family_document_import_id": "Litigation.document.89636.n0000",
        "title": "decision",
        "date": "20220914",
        "metadata": {
            "event_type": ["decision"],
            "description": ["Test summary"],
            "datetime_event_name": ["Filing Year for Action"],
        },
    }

    mapped_events = map_events(test_litigation_data, {"debug": False})
    assert expected_default_event_1 in mapped_events
    assert expected_mapped_global_event in mapped_events


def test_returns_empty_list_if_no_family_data():
    assert not map_events({}, {"debug": False})
