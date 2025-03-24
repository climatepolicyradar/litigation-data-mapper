from litigation_data_mapper.parsers.event import map_events

test_litigation_data = {
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
        },
        {
            "id": 89976,
            "type": "case",
            "acf": {
                "ccl_case_bundle": [8917],
                "ccl_docket_number": "20250065 ",
                "ccl_entity": 252,
                "ccl_filing_year_for_action": "2020",
                "ccl_case_documents": None,
            },
        },
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


expected_default_event_1 = {
    "import_id": "Litigation.event.89975.n0000",
    "family_import_id": "Litigation.family.89975.0",
    "family_document_import_id": "",
    "event_type_value": "Filing Year for Action",
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
    "event_type_value": "Filing Year for Action",
    "title": "Filing Year for Action",
    "date": "20220101",
    "metadata": {
        "event_type": ["Filing Year for Action"],
        "description": ["Filing Year for Action"],
        "datetime_event_name": ["Filing Year for Action"],
    },
}

default_context = {"debug": False, "skipped_families": []}


def test_successfully_mapped_events_include_a_default_event_per_family():
    mapped_events = map_events(test_litigation_data, default_context)
    assert expected_default_event_1 in mapped_events
    assert expected_default_event_2 in mapped_events


def test_successfully_maps_us_litigation_data_to_events():
    expected_mapped_us_event = {
        "import_id": "Litigation.event.89975.n0001",
        "family_import_id": "Litigation.family.89975.0",
        "family_document_import_id": "Litigation.document.89975.n0000",
        "event_type_value": "Petition",
        "title": "petition",
        "date": "20250227",
        "metadata": {
            "event_type": ["Petition"],
            "description": ["Test summary"],
            "datetime_event_name": ["Petition"],
        },
    }

    mapped_events = map_events(test_litigation_data, default_context)
    assert expected_mapped_us_event in mapped_events


def test_successfully_maps_global_litigation_data_to_events():
    expected_mapped_global_event = {
        "import_id": "Litigation.event.89636.n0001",
        "family_import_id": "Litigation.family.89636.0",
        "family_document_import_id": "Litigation.document.89636.n0000",
        "event_type_value": "Decision",
        "title": "decision",
        "date": "20220914",
        "metadata": {
            "event_type": ["Decision"],
            "description": ["Test summary"],
            "datetime_event_name": ["Decision"],
        },
    }

    mapped_events = map_events(test_litigation_data, default_context)
    assert expected_mapped_global_event in mapped_events


def test_returns_empty_list_if_no_us_family_data(capsys):
    assert not map_events({"global_cases": [{}]}, default_context)
    captured = capsys.readouterr()

    assert (
        "🛑 No US cases found in the data. Skipping document litigation."
        in captured.out.strip()
    )


def test_returns_empty_list_if_no_global_family_data(capsys):
    assert not map_events({"us_cases": [{}]}, default_context)
    captured = capsys.readouterr()

    assert (
        "🛑 No Global cases found in the data. Skipping document litigation."
        in captured.out.strip()
    )


def test_skips_mapping_events_if_no_case_id(capsys):
    assert not map_events(
        {"us_cases": [{}], "global_cases": [{"id": ""}]},
        default_context,
    )
    captured = capsys.readouterr()

    assert (
        "🛑 Skipping mapping events, missing case id at index 0" in captured.out.strip()
    )
    assert (
        "🛑 Skipping mapping events, missing case id at index 1" in captured.out.strip()
    )


def test_skips_mapping_events_if_family_was_previously_skipped(capsys):
    assert not map_events(
        {"us_cases": [{"id": 0}], "global_cases": [{"id": 1}]},
        {"debug": False, "skipped_families": [0, 1]},
    )
    captured = capsys.readouterr()

    assert (
        "🛑 Skipping mapping events, case_id 0 in skipped families context."
        in captured.out.strip()
    )
    assert (
        "🛑 Skipping mapping events, case_id 1 in skipped families context."
        in captured.out.strip()
    )


def test_skips_mapping_events_if_family_filing_year_not_valid(capsys):
    assert not map_events(
        {
            "us_cases": [
                {
                    "id": 0,
                    "type": "case",
                    "acf": {
                        "ccl_case_bundle": [8917],
                        "ccl_docket_number": "20250065 ",
                        "ccl_entity": 252,
                        "ccl_filing_year_for_action": "invalid",
                        "ccl_case_documents": [],
                    },
                }
            ],
            "global_cases": [{}],
        },
        default_context,
    )
    captured = capsys.readouterr()

    assert (
        "🛑 Skipping mapping events for case: 0, [invalid] is not a valid year!"
        in captured.out.strip()
    )
