from datetime import datetime

from litigation_data_mapper.datatypes import Failure, LitigationContext
from litigation_data_mapper.parsers.event import (
    get_consolidated_event_type,
    map_event,
    map_events,
)

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
    "import_id": "Sabin.event.89975.n0000",
    "family_import_id": "Sabin.family.89975.0",
    "family_document_import_id": None,
    "event_title": "Filing Year For Action",
    "event_type_value": "Filing Year For Action",
    "date": "2019-01-01",
    "metadata": {
        "event_type": ["Filing Year For Action"],
        "description": ["Filing Year For Action"],
        "datetime_event_name": ["Filing Year For Action"],
    },
}

expected_default_event_2 = {
    "import_id": "Sabin.event.89975.n0000",
    "family_import_id": "Sabin.family.89975.0",
    "family_document_import_id": None,
    "event_title": "Filing Year For Action",
    "event_type_value": "Filing Year For Action",
    "date": "2019-01-01",
    "metadata": {
        "event_type": ["Filing Year For Action"],
        "description": ["Filing Year For Action"],
        "datetime_event_name": ["Filing Year For Action"],
    },
}

last_import_date = datetime.strptime("2025-01-01T12:00:00", "%Y-%m-%dT%H:%M:%S")

default_context = LitigationContext(
    failures=[],
    debug=True,
    last_import_date=last_import_date,
    get_modified_data=False,
    case_bundles={},
    skipped_documents=[],
    skipped_families=[],
)


def test_successfully_mapped_events_include_a_default_event_per_family():
    mapped_events = map_events(test_litigation_data, default_context)
    assert expected_default_event_1 in mapped_events
    assert expected_default_event_2 in mapped_events


def test_maps_action_taken_to_event_metadata():
    doc = {
        "ccl_document_type": "petition",
        "ccl_filing_date": "20250227",
        "ccl_file": 89977,
        "ccl_document_headline": "",
        "ccl_document_summary": "Test summary",
        "ccl_outcome": "This is the action taken",
    }

    mapped_event = map_event(
        doc,
        "case",
        "Event.import_id",
        "Sabin.family.import_id.0",
        1,
        "2025-02-27",
    )

    assert not isinstance(mapped_event, Failure)
    assert mapped_event["metadata"]["action_taken"] == ["This is the action taken"]


def test_action_taken_is_empty_if_global_case_document():
    doc = {
        "ccl_nonus_document_type": "decision",
        "ccl_nonus_filing_date": "20220914",
        "ccl_nonus_file": 89637,
        "ccl_nonus_document_summary": "Test summary",
    }

    mapped_event = map_event(
        doc,
        "non_us_case",
        "Event.import_id",
        "Sabin.family.import_id.0",
        1,
        "2022-09-14",
    )

    assert not isinstance(mapped_event, Failure)
    assert mapped_event["metadata"]["action_taken"] == []


def test_successfully_maps_us_litigation_data_to_events():
    expected_mapped_us_event = {
        "import_id": "Sabin.event.89975.n0001",
        "family_import_id": "Sabin.family.89975.0",
        "family_document_import_id": "Sabin.document.89975.89977",
        "event_type_value": "Petition",
        "event_title": "petition",
        "date": "2025-02-27",
        "metadata": {
            "action_taken": ["Test outcome"],
            "event_type": ["Petition"],
            "description": ["Test summary"],
            "datetime_event_name": ["Filing Year For Action"],
        },
    }
    mapped_events = map_events(test_litigation_data, default_context)
    assert expected_mapped_us_event in mapped_events


def test_successfully_maps_global_litigation_data_to_events():
    expected_mapped_global_event = {
        "import_id": "Sabin.event.89636.n0001",
        "family_import_id": "Sabin.family.89636.0",
        "family_document_import_id": "Sabin.document.89636.89637",
        "event_type_value": "Decision",
        "event_title": "decision",
        "date": "2022-09-14",
        "metadata": {
            "action_taken": [],
            "event_type": ["Decision"],
            "description": ["Test summary"],
            "datetime_event_name": ["Filing Year For Action"],
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
    assert (
        map_events(
            {"us_cases": [{}], "global_cases": [{"id": ""}]},
            default_context,
        )
        == []
    )
    assert (
        Failure(
            id=None,
            type="case",
            reason="Does not contain a case id at index (0). Mapping events.",
        )
        in default_context.failures
    )
    assert (
        Failure(
            id=None,
            type="case",
            reason="Does not contain a case id at index (1). Mapping events.",
        )
        in default_context.failures
    )

    captured = capsys.readouterr()

    assert (
        "Some events have been skipped during the mapping process, check failures log."
        in captured.out.strip()
    )


def test_skips_mapping_events_if_family_was_previously_skipped():
    context = LitigationContext(
        failures=[],
        debug=True,
        last_import_date=last_import_date,
        get_modified_data=False,
        case_bundles={},
        skipped_documents=[],
        skipped_families=[0, 1],
    )
    events = map_events(
        {"us_cases": [{"id": 0}], "global_cases": [{"id": 1}]},
        context,
    )

    assert events == []


def test_skips_mapping_events_if_family_filing_year_not_valid(capsys):
    context = LitigationContext(
        failures=[],
        debug=True,
        last_import_date=last_import_date,
        get_modified_data=False,
        case_bundles={},
        skipped_documents=[],
        skipped_families=[],
    )
    events = map_events(
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
        context,
    )
    assert events == []
    assert (
        Failure(
            id=0,
            type="event",
            reason="Event does not have valid filing year for action [invalid]",
        )
        in context.failures
    )
    captured = capsys.readouterr()
    assert (
        "Some events have been skipped during the mapping process, check failures log."
        in captured.out.strip()
    )


def test_skips_mapping_events_if_no_documents_exists_to_parse_earliest_filing_date(
    capsys,
):
    context = LitigationContext(
        failures=[],
        debug=True,
        last_import_date=last_import_date,
        get_modified_data=False,
        case_bundles={},
        skipped_documents=[],
        skipped_families=[],
    )
    events = map_events(
        {
            "us_cases": [
                {
                    "id": 0,
                    "type": "case",
                    "acf": {
                        "ccl_case_bundle": [8917],
                        "ccl_docket_number": "20250065",
                        "ccl_entity": 252,
                        "ccl_filing_year_for_action": "",
                        "ccl_case_documents": [],
                    },
                }
            ],
            "global_cases": [{}],
        },
        context,
    )
    assert events == []
    assert (
        Failure(
            id=0,
            type="event",
            reason="Case does not have valid events to parse earliest filing dates []",
        )
        in context.failures
    )
    captured = capsys.readouterr()
    assert (
        "Some events have been skipped during the mapping process, check failures log."
        in captured.out.strip()
    )


def test_skips_mapping_events_if_earliest_filing_date_can_not_be_parsed(capsys):
    context = LitigationContext(
        failures=[],
        debug=True,
        last_import_date=last_import_date,
        get_modified_data=False,
        case_bundles={},
        skipped_documents=[],
        skipped_families=[],
    )
    events = map_events(
        {
            "us_cases": [
                {
                    "id": 0,
                    "type": "case",
                    "acf": {
                        "ccl_case_bundle": [8917],
                        "ccl_docket_number": "20250065",
                        "ccl_entity": 252,
                        "ccl_filing_year_for_action": "",
                        "ccl_case_documents": [
                            {
                                "ccl_document_type": "petition",
                                "ccl_filing_date": "",
                                "ccl_file": 89977,
                                "ccl_document_headline": "",
                                "ccl_document_summary": "",
                                "ccl_outcome": "",
                            }
                        ],
                    },
                }
            ],
            "global_cases": [{}],
        },
        context,
    )
    assert events == []
    assert (
        Failure(
            id=0,
            type="event",
            reason="Case does not have valid events to parse earliest filing dates []",
        )
        in context.failures
    )
    captured = capsys.readouterr()
    assert (
        "Some events have been skipped during the mapping process, check failures log."
        in captured.out.strip()
    )


def test_skips_mapping_event_if_document_id_in_skipped_context():
    document_file_id = test_litigation_data["us_cases"][0]["acf"]["ccl_case_documents"][
        0
    ]["ccl_file"]

    default_context.skipped_documents.append(document_file_id)
    mapped_events = map_events(test_litigation_data, default_context)

    for event in mapped_events:
        if event["family_document_import_id"] is not None:
            assert str(document_file_id) not in event["family_document_import_id"]


def test_get_consolidated_event_type_valid_mappings():
    """Test that get_consolidated_event_type returns correct consolidated types for valid inputs."""

    test_cases = [
        ("Administrative Order", "Order"),
        ("Affidavit", "Affidavit/Declaration"),
        ("Affirmation", "Affidavit/Declaration"),
        ("Amicus Brief", "Amicus Motion/Brief"),
        ("Amicus Motion", "Amicus Motion/Brief"),
        ("Answer", "Answer"),
        ("Appeal", "Appeal"),
        ("Brief", "Brief"),
        ("Complaint", "Complaint"),
        ("Motion", "Motion"),
        ("Motion For Summary Judgment", "Motion For Summary Judgment"),
        ("Motion to Dismiss", "Motion To Dismiss"),
        ("Petition", "Petition"),
        ("Decision", "Decision"),
        ("Order", "Decision"),
        ("Settlement Agreement", "Settlement Agreement"),
    ]

    for original_type, expected_consolidated in test_cases:
        result = get_consolidated_event_type(original_type)
        assert (
            result == expected_consolidated
        ), f"Expected '{expected_consolidated}' for '{original_type}', got '{result}'"


def test_map_event_with_consolidated_event_type():
    """Test that map_event correctly uses consolidated event types."""

    doc = {
        "ccl_document_type": "Administrative Order",
        "ccl_filing_date": "20250227",
        "ccl_file": 89977,
        "ccl_document_headline": "",
        "ccl_document_summary": "Test administrative order summary",
        "ccl_outcome": "Order issued",
    }

    mapped_event = map_event(
        doc,
        "case",
        "Event.import_id",
        "Sabin.family.import_id.0",
        1,
        "2025-02-27",
    )

    assert not isinstance(mapped_event, Failure)
    assert mapped_event["event_type_value"] == "Order"  # Should be consolidated type
    assert (
        mapped_event["event_title"] == "Administrative Order"
    )  # Should be original type
    assert mapped_event["metadata"]["event_type"] == [
        "Order"
    ]  # Should be consolidated type


def test_map_event_invalid_event_type_returns_failure():
    """Test that map_event returns Failure for invalid document types."""

    doc = {
        "ccl_document_type": "Invalid Document Type",
        "ccl_filing_date": "20250227",
        "ccl_file": 89977,
        "ccl_document_headline": "",
        "ccl_document_summary": "Test summary",
    }

    result = map_event(
        doc,
        "case",
        "Event.import_id",
        "Sabin.family.import_id.0",
        1,
        "2025-02-27",
    )

    assert isinstance(result, Failure)
    assert result.type == "event"
    assert "invalid event type" in result.reason.lower()
    assert "Invalid Document Type" in result.reason
