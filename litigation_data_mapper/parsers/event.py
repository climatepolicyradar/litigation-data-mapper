from datetime import datetime
from typing import Any

import click

from litigation_data_mapper.datatypes import Failure, LitigationContext
from litigation_data_mapper.enums.events import DOC_TYPE_TO_EVENT_TYPE, DocType
from litigation_data_mapper.parsers.helpers import initialise_counter, write_error_log
from litigation_data_mapper.parsers.utils import convert_year_to_dmy

DOC_TYPES = {doc.value.lower(): doc for doc in DocType}


def get_earliest_event_filing_date(documents: dict, documents_key: str) -> str | None:
    """Returns the earliest filing date from a family case's documents.

    :param dict family: The family case data containing documents.
    :param str documents_key: The key to access the documents in the family case data.
    :return str | None: The earliest filing date in 'YYYY-MM-DD' format, or None if no valid dates are found.
    """

    if not documents:
        return None

    date_key = (
        "ccl_filing_date"
        if documents_key == "ccl_case_documents"
        else "ccl_nonus_filing_date"
    )

    valid_dates = []
    for doc in documents:
        date_str = doc.get(date_key)
        if not date_str:
            continue
        try:
            dt = datetime.strptime(date_str, "%Y%m%d")
            valid_dates.append(dt)
        except (ValueError, TypeError):
            continue

    if not valid_dates:
        return None

    earliest_date = min(valid_dates)
    return earliest_date.strftime("%Y-%m-%d")


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

    normalised_doc_type = doc_type.strip().lower()

    type = DOC_TYPES.get(normalised_doc_type)
    if not type:
        return None

    event_type = DOC_TYPE_TO_EVENT_TYPE.get(type)

    return event_type.value if event_type else None


def map_event(
    doc: dict,
    case_type: str,
    event_import_id: str,
    family_import_id: str,
    case_id: int,
    fallback_date: str,
) -> dict[str, Any] | Failure:
    """Processes an event and maps it to the internal data structure.

    :param dict doc: The case document data.
    :param str case_type: The type of the case the event is linked to.
    :param dict[str, Any] context: The context of the litigation project import.
    :param str event_import_id: A generated id for the event being mapped.
    :param str family_import_id: A generated id for the family the mapped event is linked to.
    :param int case_id: The unique identifier for the case, used to link events to the correct case.
    :param str fallback_date: A fallback date to use if the document does not have a filing date.
    :return Optional[dict]: A mapped event in the 'destination' format described in the Litigation Data Mapper Google Sheet, or empty list if no events are found or None.
    """

    litigation_doc_type = doc[
        get_key(
            case_type,
            "ccl_document_type",
            "ccl_nonus_document_type",
        )
    ]
    event_type = get_event_type(litigation_doc_type)

    if event_type is None:
        return Failure(
            id=case_id,
            type="event",
            reason=f"Event has invalid event type: ({litigation_doc_type})",
        )

    document_id_key = "ccl_file" if case_type == "case" else "ccl_nonus_file"
    document_id = doc.get(document_id_key)

    document_import_id = None
    # Not all documents will have file ids, or related document files, for instances such as
    # motion to file proceedings.
    if isinstance(document_id, int):
        document_import_id = f"Sabin.document.{case_id}.{document_id}"

    date = doc[get_key(case_type, "ccl_filing_date", "ccl_nonus_filing_date")]
    if date:
        parsed_date = datetime.strptime(date, "%Y%m%d").strftime("%Y-%m-%d")
    else:
        parsed_date = fallback_date

    event_data = {
        "import_id": event_import_id,
        "family_import_id": family_import_id,
        "family_document_import_id": document_import_id,
        "event_type_value": event_type,
        "event_title": doc[
            get_key(case_type, "ccl_document_type", "ccl_nonus_document_type")
        ],
        "date": parsed_date,
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
    context: LitigationContext,
) -> list[dict[str, Any]] | Failure:
    """Processes the family- and document-related case events and maps them to the internal data structure.

    This function transforms family case data into our internal data modelling structure.
    It returns a list of mapped family events, each represented as a dictionary matching the required schema.

    :param dict family: The family case related data, including family details and related documents.
    :param int case_id: The unique identifier for the case, used to link events to the correct case.
    :param dict[str, int] event_family_counter: A dictionary that tracks the count of events types for each family case.
    :param LitigationContext context: The context of the litigation project import.
    :return list[dict[str, Any] | Failure: A list of mapped family case events in the 'destination' format described in the Litigation Data Mapper Google Sheet, or Failure if case contains missing data.
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
    if filing_date:
        filing_year = convert_year_to_dmy(filing_date)
        if not filing_year:
            return Failure(
                id=case_id,
                type="event",
                reason=f"Event does not have valid filing year for action [{filing_date}]",
            )
    else:
        earliest_date = get_earliest_event_filing_date(documents, documents_key)
        if not earliest_date:
            return Failure(
                id=case_id,
                type="event",
                reason=f"Case does not have valid events to parse earliest filing dates [{filing_date}]",
            )
        filing_year = earliest_date

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
            document_id_key = "ccl_file" if case_type == "case" else "ccl_nonus_file"
            document_id = doc.get(document_id_key)

            if document_id in context.skipped_documents:
                continue

            event_import_id = (
                f"Sabin.event.{case_id}.n{event_family_counter[family_import_id]:04}"
            )
            event_data = map_event(
                doc,
                str(case_type),
                event_import_id,
                family_import_id,
                case_id,
                filing_year,
            )
            if isinstance(event_data, Failure):
                context.failures.append(event_data)
                continue

            family_events.append(event_data)
            event_family_counter[family_import_id] += 1
    return family_events


def map_events(
    events_data: dict[str, Any], context: LitigationContext
) -> list[dict[str, Any]]:
    """Maps the litigation case event information to the internal data structure.

    This function transforms event data, which the Sabin Centre refers to as
    case events, into our internal data modelling structure. It returns a list of
    mapped events, each represented as a dictionary matching the required schema.

     :parm dict[str, Any] events_data: The case related data, structured as global cases,
        Us cases.
    :param  LitigationContext context: The context of the litigation project import.
    :return list[dict[str, Any]]: A list of litigation case events in
        the 'destination' format described in the Litigation Data Mapper Google
        Sheet.
    """
    if context.debug:
        click.echo("📝 Wrangling litigation event data.")

    failures_count = len(context.failures)

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
        if not isinstance(case_id, int):
            context.failures.append(
                Failure(
                    id=None,
                    type="case",
                    reason=f"Does not contain a case id at index ({index}). Mapping events.",
                )
            )
            continue
        if case_id in context.skipped_families:
            continue

        result = process_family_events(family, case_id, event_family_counter, context)

        if isinstance(result, Failure):
            context.failures.append(result)
        else:
            mapped_events.extend(result)

    if len(context.failures) > failures_count:
        click.echo(
            "🛑 Some events have been skipped during the mapping process, check failures log."
        )

    write_error_log(context)

    return mapped_events
