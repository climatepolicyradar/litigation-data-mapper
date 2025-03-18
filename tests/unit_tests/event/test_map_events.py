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
        ]
    }
}


expected_default_event = {
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


def test_successfully_mapped_us_events_include_default_event():
    assert expected_default_event in map_events(test_litigation_data, {"debug": False})


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

    assert [expected_default_event, expected_mapped_us_event] == map_events(
        test_litigation_data, {"debug": False}
    )
