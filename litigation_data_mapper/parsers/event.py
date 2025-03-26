from typing import Any

import click

from litigation_data_mapper.enums.events import EventType
from litigation_data_mapper.parsers.helpers import initialise_counter
from litigation_data_mapper.parsers.utils import convert_year_to_dmy

EVENT_TYPES = {event.value.lower(): event for event in EventType}


def get_key(case_type, case_key: str, nonus_key: str) -> str:
    """Returns the appropriate key based on the case type."""
    return case_key if case_type == "case" else nonus_key


def default_event(
    case_id: int, filing_year: str, family_import_id: str
) -> dict[str, Any]:
    """
    Generates a default first event for a family based on case id.

    :param int case_id: The unique identifier for the case, used to link events to the correct case.
    :return dict[str, Any]: A mapped default family case event in the 'destination' format described in the Litigation Data Mapper Google Sheet.
    """

    return {
        "import_id": f"Sabin.event.{case_id}.n{0:04}",
        "family_import_id": family_import_id,
        "family_document_import_id": None,
        "event_title": "Filing Year For Action",
        "event_type_value": "Filing Year For Action",
        "date": filing_year,
        "metadata": {
            "event_type": ["Filing Year For Action"],
            "description": ["Filing Year For Action"],
            "datetime_event_name": ["Filing Year For Action"],
        },
    }


def get_event_type(doc_type: str) -> str | None:
    """Retrieves the event type value based on the provided document type.

    :param str doc_type: The document type for which to retrieve the event type.
    :return str | None: The corresponding event type value if found, otherwise None.
    """

    event_type = EVENT_TYPES.get(doc_type.lower())
    return event_type.value if event_type else None


def map_event(doc, case_type, context, event_import_id, family_import_id, case_id):
    litigation_doc_type = doc[
        get_key(
            case_type,
            "ccl_document_type",
            "ccl_nonus_document_type",
        )
    ]
    event_type = get_event_type(litigation_doc_type)
    if event_type is None:
        click.echo(
            f"🛑 Skipping event for case ({case_id}): {litigation_doc_type} is not a valid event type!"
        )
        return None

    document_id_key = "ccl_file" if case_type == "case" else "ccl_nonus_file"
    document_id = doc.get(document_id_key)

    if document_id in context["skipped_documents"]:
        click.echo(f"🛑 Skipping event: document {document_id} is in skipped context")
        return None

    document_import_id = None
    # Not all documents will have file ids, or related document files, for instances such as
    # motion to file proceedings.
    if isinstance(document_id, int):
        document_import_id = f"Sabin.document.{case_id}.{document_id}"

    event_data = {
        "import_id": event_import_id,
        "family_import_id": family_import_id,
        "family_document_import_id": document_import_id,
        "event_type_value": event_type,
        "event_title": doc[
            get_key(case_type, "ccl_document_type", "ccl_nonus_document_type")
        ],
        "date": doc[get_key(case_type, "ccl_filing_date", "ccl_nonus_filing_date")],
        "metadata": {
            "event_type": [event_type],
            "description": [
                doc[
                    get_key(
                        case_type,
                        "ccl_document_summary",
                        "ccl_nonus_document_summary",
                    )
                ]
            ],
            "datetime_event_name": ["Filing Year For Action"],
        },
    }

    return event_data


def process_family_events(
    family: dict,
    case_id: int,
    event_family_counter: dict[str, int],
    context: dict[str, Any],
) -> list[dict[str, Any]]:
    """Processes the family- and document-related case events and maps them to the internal data structure.

    This function transforms family case data into our internal data modelling structure.
    It returns a list of mapped family events, each represented as a dictionary matching the required schema.

    :param dict family: The family case related data, including family details and related documents.
    :param int case_id: The unique identifier for the case, used to link events to the correct case.
    :param dict[str, int] event_family_counter: A dictionary that tracks the count of events types for each family case.
    :param dict[str, Any] context: The context of the litigation project import.
    :return list[dict[str, Any]]: A list of mapped family case events in the 'destination' format described in the Litigation Data Mapper Google Sheet, or empty list if no events are found.
    """
    case_type = family.get("type")

    family_events = []
    family_import_id = f"Sabin.family.{case_id}.0"
    initialise_counter(event_family_counter, family_import_id)

    documents_key = (
        "ccl_case_documents" if case_type == "case" else "ccl_nonus_case_documents"
    )
    documents = family.get("acf", {}).get(documents_key, [])

    filing_date = family.get("acf", {})[
        get_key(
            case_type,
            "ccl_filing_year_for_action",
            "ccl_nonus_filing_year_for_action",
        )
    ]
    try:
        filing_year = convert_year_to_dmy(filing_date)
    except ValueError:
        click.echo(
            f"🛑 Skipping mapping events for case: {case_id}, [{filing_date}] is not a valid year!"
        )
        return []

    family_events.append(
        default_event(
            case_id,
            filing_year,
            family_import_id,
        )
    )
    event_family_counter[family_import_id] += 1

    if documents:
        for doc in documents:
            event_import_id = (
                f"Sabin.event.{case_id}.n{event_family_counter[family_import_id]:04}"
            )
            event_data = map_event(
                doc, case_type, context, event_import_id, family_import_id, case_id
            )
            if not event_data:
                continue

            family_events.append(event_data)
            event_family_counter[family_import_id] += 1
    return family_events


def map_events(
    events_data: dict[str, Any], context: dict[str, Any]
) -> list[dict[str, Any]]:
    """Maps the litigation case event information to the internal data structure.

    This function transforms event data, which the Sabin Centre refers to as
    case events, into our internal data modelling structure. It returns a list of
    mapped events, each represented as a dictionary matching the required schema.

     :parm dict[str, Any] events_data: The case related data, structured as global cases,
        Us cases.
    :param  dict[str, Any] context: The context of the litigation project import.
    :return list[dict[str, Any]]: A list of litigation case events in
        the 'destination' format described in the Litigation Data Mapper Google
        Sheet.
    """
    if context["debug"]:
        click.echo("📝 No Litigation event data to wrangle.")

    us_cases = events_data.get("us_cases", [])
    global_cases = events_data.get("global_cases", [])

    if not us_cases or not global_cases:
        missing_dataset = "Global" if not global_cases else "US"
        click.echo(
            f"🛑 No {missing_dataset} cases found in the data. Skipping document litigation."
        )
        return []

    families = us_cases + global_cases

    event_family_counter = {}
    mapped_events = []

    for index, family in enumerate(families):
        case_id = family.get("id")
        if case_id is None or case_id == "":
            click.echo(f"🛑 Skipping mapping events, missing case id at index {index}.")
            continue

        if case_id in context["skipped_families"]:
            click.echo(
                f"🛑 Skipping mapping events, case_id {case_id} in skipped families context."
            )
            continue

        result = process_family_events(family, case_id, event_family_counter, context)
        mapped_events.extend(result)

    return mapped_events
