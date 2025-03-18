from typing import Any

import click

from litigation_data_mapper.parsers.helpers import initialise_counter
from litigation_data_mapper.parsers.utils import convert_year_to_dmy


def process_family_events(
    family: dict,
    case_id: int,
    event_family_counter: dict[str, int],
    document_family_counter: dict[str, int],
) -> list[dict[str, Any]]:
    """Processes the family- and document-related case events and maps them to the internal data structure.

    This function transforms family case data into our internal data modelling structure.
    It returns a list of mapped family events, each represented as a dictionary matching the required schema.

    :param dict family: The family case related data, including family details and related documents.
    :param int case_id: The unique identifier for the case, used to link events to the correct case.
    :param dict[str, int] event_family_counter: A dictionary that tracks the count of events types for each family case.
    :param dict[str, int] document_family_counter: A dictionary that tracks the count of document types for each family case.
    :return list[dict[str, Any]]: A list of mapped family case events in the 'destination' format described in the Litigation Data Mapper Google Sheet, or empty list if no events are found.
    """
    case_type = family.get("type")

    family_events = []
    family_import_id = f"Litigation.family.{case_id}.0"
    initialise_counter(event_family_counter, family_import_id)
    initialise_counter(document_family_counter, family_import_id)

    documents_key = (
        "ccl_case_documents" if case_type == "case" else "ccl_nonus_case_documents"
    )
    documents = family.get("acf", {}).get(documents_key, [])

    # Add default event to every valid family
    family_events.append(
        {
            "import_id": f"Litigation.event.{case_id}.n{event_family_counter[family_import_id]:04}",
            "family_import_id": family_import_id,
            "family_document_import_id": "",
            "title": "Filing Year for Action",
            "date": convert_year_to_dmy(
                family.get("acf", {}).get(
                    (
                        "ccl_filing_year_for_action"
                        if case_type == "case"
                        else "ccl_nonus_filing_year_for_action"
                    ),
                    [],
                )
            ),
            "metadata": {
                "event_type": ["Filing Year for Action"],
                "description": ["Filing Year for Action"],
                "datetime_event_name": ["Filing Year for Action"],
            },
        }
    )
    event_family_counter[family_import_id] += 1

    for doc in documents:
        event_import_id = (
            f"Litigation.event.{case_id}.n{event_family_counter[family_import_id]:04}"
        )
        family_events.append(
            {
                "import_id": event_import_id,
                "family_import_id": family_import_id,
                "family_document_import_id": f"Litigation.document.{case_id}.n{document_family_counter[family_import_id]:04}",
                "title": doc[
                    (
                        "ccl_document_type"
                        if case_type == "case"
                        else "ccl_nonus_document_type"
                    )
                ],
                "date": doc[
                    (
                        "ccl_filing_date"
                        if case_type == "case"
                        else "ccl_nonus_filing_date"
                    )
                ],
                "metadata": {
                    "event_type": [
                        doc[
                            (
                                "ccl_document_type"
                                if case_type == "case"
                                else "ccl_nonus_document_type"
                            )
                        ]
                    ],
                    "description": [
                        doc[
                            (
                                "ccl_document_summary"
                                if case_type == "case"
                                else "ccl_nonus_document_summary"
                            )
                        ]
                    ],
                    "datetime_event_name": ["Filing Year for Action"],
                },
            }
        )
        event_family_counter[family_import_id] += 1
        document_family_counter[family_import_id] += 1
    return family_events


def map_events(
    events_data: dict[str, Any], context: dict[str, Any]
) -> list[dict[str, Any]]:
    """Maps the litigation case event information to the internal data structure.

    This function transforms event data, which the Sabin Centre refers to as
    case events, into our internal data modelling structure. It returns a list of
    mapped events, each represented as a dictionary matching the required schema.

    :param  dict[str, Any] context: The context of the litigation project import.
    :return list[dict[str, Any]]: A list of litigation case events in
        the 'destination' format described in the Litigation Data Mapper Google
        Sheet.
    """
    if context["debug"]:
        click.echo("📝 No Litigation event data to wrangle.")

    us_cases = events_data.get("families", {}).get("us_cases", [])
    global_cases = events_data.get("families", {}).get("global_cases", [])

    families = us_cases + global_cases
    event_family_counter = {}
    document_family_counter = {}
    mapped_events = []

    for family in families:
        case_id = family.get("id")
        result = process_family_events(
            family, case_id, event_family_counter, document_family_counter
        )
        mapped_events.extend(result)

    return mapped_events
