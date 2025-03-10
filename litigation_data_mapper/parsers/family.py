from typing import Any, Optional

import click

from litigation_data_mapper.parsers.helpers import (
    map_global_jurisdictions,
    parse_document_filing_date,
    return_empty_values,
)


def process_global_case_metadata(
    family_data: dict[str, Any], case_id: int
) -> Optional[dict[str, Any]]:
    """
    Maps the metadata of a global case to the internal family metadata structure.

    :param dict family_data: The family data containing the case metadata.
    :param int case_id: The ID of the case.
    :return Optional[dict[str, Any]]: The mapped family metadata, or None if any required fields are missing.
    """

    original_case_name = family_data.get("acf", {}).get("ccl_nonus_case_name")
    core_object = family_data.get("acf", {}).get("ccl_nonus_core_object")
    status = family_data.get("acf", {}).get("ccl_nonus_status")
    docket_number = family_data.get("acf", {}).get("ccl_nonus_reporter_info")

    empty_values = return_empty_values(
        [
            ("original_case_name", original_case_name),
            ("core_object", core_object),
            ("status", status),
            ("reporter_info", docket_number),
        ]
    )

    if empty_values:
        click.echo(
            f"🛑 Skipping global case_id {case_id}, missing family metadata: {', '.join(empty_values)}"
        )
        return None

    family_metadata = {
        "original_case_name": [original_case_name],
        "id": [case_id],
        "status": [status],
        "case_number": [docket_number],
        "core_object": [core_object],
    }

    return family_metadata


def process_global_case_data(
    family_data: dict[str, Any], geographies: list[str], case_id: int
) -> Optional[dict[str, Any]]:
    """
    Maps the data of a global case to the internal family structure.

    :param dict family_data: The family data containing the case information.
    :param list[str] geographies: The ISO codes of the geographies associated with the case.
    :param int case_id: The ID of the case.

    :return Optional[dict[str, Any]]: The mapped family data, or None if any required fields are missing.
    """

    family_metadata = process_global_case_metadata(family_data, case_id)

    title = family_data.get("title", {}).get("rendered")
    summary = family_data.get("acf", {}).get("ccl_nonus_summary")

    empty_values = return_empty_values([("title", title), ("summary", summary)])

    if empty_values:
        click.echo(
            f"🛑 Skipping global case_id {case_id}, missing: {', '.join(empty_values)}"
        )
        return None

    if not family_metadata:
        return None

    global_family = {
        "import_id": f"Litigation.family.{case_id}.0",
        "title": title,
        "summary": summary,
        "geographies": geographies,
        "metadata": family_metadata,
        "collections": [],
    }

    return global_family


def get_latest_document_status(family: dict[str, Any]) -> Optional[str]:
    """
    Retrieve the status of the latest document in the case, based on the filing date.

    This function retrieves a list of documents from the given case and determines which
    document has the most recent filing date by. If no documents are found, it returns None.

    :param dict family: The family dictionary containing document information.
    :return str: The status of the latest document (from the 'ccl_outcome' field),
                 or an empty string if no documents are found.
    """

    documents = family.get("acf", {}).get("ccl_case_documents", [])

    if not documents:
        return None

    latest_document_in_case = max(
        documents, key=lambda doc: parse_document_filing_date(doc)
    )

    return latest_document_in_case.get("ccl_outcome")


def process_us_case_metadata(family_data, case_id: int) -> Optional[dict[str, Any]]:
    """
    Maps the metadata of a US case to the internal family metadata structure.

    :param dict family_data: The family data containing the case metadata.
    :param int case_id: The ID of the case.
    :return dict[str, Any]: The mapped family metadata, or None if any required fields are missing.
    """
    docket_number = family_data.get("acf", {}).get("ccl_docket_number")
    status = get_latest_document_status(family_data)

    empty_values = return_empty_values(
        [("docket_number", docket_number), ("case documents", status)]
    )

    if empty_values:
        click.echo(
            f"🛑 Skipping US case_id {case_id}, missing family metadata: {', '.join(empty_values)}"
        )
        return None

    family_metadata = {
        "original_case_name": [],
        "id": [case_id],
        "status": [status],
        "case_number": [docket_number],
        "core_object": [],
    }

    return family_metadata


def process_us_case_data(
    family_data: dict[str, Any], case_id: int
) -> Optional[dict[str, Any]]:
    """
    Maps the data of a US case to the internal family structure.

    :param dict family_data: The family data containing the case information.
    :param int case_id: The ID of the case.

    :return dict[str, Any]: The mapped family data, or None if any required fields are missing.
    """

    family_metadata = process_us_case_metadata(family_data, case_id)
    title = family_data.get("title", {}).get("rendered")
    bundle_ids = family_data.get("acf", {}).get("ccl_case_bundle", [])

    empty_values = return_empty_values([("title", title), ("bundle_ids", bundle_ids)])

    if empty_values:
        click.echo(
            f"🛑 Skipping US case_id {case_id}, missing {', '.join(empty_values)}"
        )
        return None

    collections = [f"Litigation.collection.{id}.0" for id in bundle_ids]

    if not family_metadata:
        return None

    us_family = {
        "import_id": f"Litigation.family.{case_id}.0",
        "title": title,
        "summary": "",  # Note this is a required field, so this will fail on validation
        "geographies": ["USA"],
        "metadata": family_metadata,
        "collections": collections,
    }

    return us_family


def get_jurisdiction_iso_codes(
    family: dict[str, Any], mapped_jurisdictions: dict[str, dict[str, str]]
) -> list[str]:
    """Retrieve the ISO codes for jurisdictions specified in the family data.

    This function checks the jurisdiction IDs in the provided family data against
    a mapping of jurisdictions to their ISO codes. It returns a list of ISO codes
    for the valid jurisdiction IDs. If no valid jurisdiction IDs are found, it
    returns a default value.

    :param family: A dictionary containing family data, which includes jurisdiction IDs.
    :param mapped_jurisdictions: A dictionary mapping jurisdiction IDs to their ISO codes.
    :return: A list of ISO codes for the jurisdictions, or a default value if none are found.
    """

    # International : XAA

    jurisdiction_ids = family.get("jurisdiction", [])
    iso_codes = []

    for jurisdiction_id in jurisdiction_ids:
        if jurisdiction_id in mapped_jurisdictions:
            iso_codes.append(mapped_jurisdictions[jurisdiction_id]["iso"])

    return iso_codes if iso_codes else ["XAA"]


def map_families(
    families_data: dict[str, list[dict[str, Any]]], debug: bool
) -> list[Optional[dict[str, Any]]]:
    """Maps the litigation case information to the internal data structure.

    This function transforms family data, which the Sabin Centre refers to as
    cases, into our internal data modelling structure. It returns a list of
    mapped families, each represented as a dictionary matching the required schema.

    :param bool debug: Flag indicating whether to enable debug mode. When enabled, debug
        messages are logged for troubleshooting..
    :return list[Optional[dict[str, Any]]]: A list of litigation families in
        the 'destination' format described in the Litigation Data Mapper Google
        Sheet.
    """
    if debug:
        click.echo("📝 No Litigation family data to wrangle.")

    global_cases = families_data.get("global_cases", [])
    us_cases = families_data.get("us_cases", [])
    jurisdictions = families_data.get("jurisdictions", [])

    mapped_jurisdictions = map_global_jurisdictions(jurisdictions)

    if not global_cases or not us_cases:
        missing_dataset = "global" if not global_cases else "US"
        click.echo(
            f"🛑 No {missing_dataset} cases found in the data. Skipping family litigation."
        )
        return []

    if not jurisdictions:
        click.echo(
            "🛑 No jurisdictions provided in the family data. Skipping family litigation."
        )
        return []

    mapped_families = []

    for index, data in enumerate(us_cases):
        case_id = data.get("id")
        if not case_id:
            click.echo(
                f"🛑 Skipping US case at index: {index} as it does not contain a case id"
            )
            continue

        result = process_us_case_data(data, case_id)

        if result:
            mapped_families.append(result)

    for index, data in enumerate(global_cases):
        case_id = data.get("id")
        if not case_id:
            click.echo(
                f"🛑 Skipping global case at index: {index} as it does not contain a case id"
            )
            continue
        geographies = get_jurisdiction_iso_codes(data, mapped_jurisdictions)
        result = process_global_case_data(data, geographies, case_id)

        if result:
            mapped_families.append(result)

    return mapped_families
