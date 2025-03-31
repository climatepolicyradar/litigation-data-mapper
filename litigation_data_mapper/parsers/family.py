from typing import Any, Optional

import click

from litigation_data_mapper.context import LitigationContext
from litigation_data_mapper.parsers.helpers import (
    map_global_jurisdictions,
    return_empty_values,
)
from litigation_data_mapper.parsers.utils import to_us_state_iso


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
    case_number = family_data.get("acf", {}).get("ccl_nonus_reporter_info")

    empty_values = return_empty_values(
        [
            ("core_object", core_object),
            ("status", status),
            ("reporter_info", case_number),
        ]
    )

    if empty_values:
        click.echo(
            f"🛑 Skipping global case ({case_id}), missing family metadata: {', '.join(empty_values)}"
        )
        return None

    family_metadata = {
        "original_case_name": [original_case_name] if original_case_name else [],
        "id": [str(case_id)],
        "status": [status],
        "case_number": [case_number],
        "core_object": [core_object],
    }

    return family_metadata


def process_global_case_data(
    family_data: dict[str, Any], geographies: list[str], case_id: int
) -> Optional[dict[str, Any]]:
    """
    Maps the data of a global case to the internal family structure.

    :param dict[str, Any] family_data: The family data containing the case information.
    :param list[str] geographies: The list of geography codes for the case.
    :param int case_id: The ID of the case.
    :return Optional[dict[str, Any]]: The mapped family data, or None if any required fields are missing.
    """
    family_metadata = process_global_case_metadata(family_data, case_id)
    title = family_data.get("title", {}).get("rendered")
    status = get_latest_document_status(family_data)

    if not family_metadata or not title or not status:
        return None

    global_family = {
        "import_id": f"Sabin.family.{case_id}.0",
        "title": title,
        "summary": " ",
        "geographies": geographies,
        "metadata": family_metadata,
        "collections": [],
        "category": "Litigation",
    }

    return global_family


def get_latest_document_status(family: dict[str, Any]) -> Optional[str]:
    """
    Gets the latest document status from the family data.

    :param dict[str, Any] family: The family data containing the case information.
    :return Optional[str]: The latest document status, or None if not found.
    """
    documents_key = (
        "ccl_case_documents"
        if family.get("type") == "case"
        else "ccl_nonus_case_documents"
    )
    documents = family.get("acf", {}).get(documents_key, [])

    if not documents:
        return None

    latest_doc = documents[-1]
    status_key = (
        "ccl_document_status"
        if family.get("type") == "case"
        else "ccl_nonus_document_status"
    )
    return latest_doc.get(status_key)


def process_us_case_metadata(
    family_data: dict[str, Any], case_id: int
) -> Optional[dict[str, Any]]:
    """
    Maps the metadata of a US case to the internal family metadata structure.

    :param dict[str, Any] family_data: The family data containing the case metadata.
    :param int case_id: The ID of the case.
    :return Optional[dict[str, Any]]: The mapped family metadata, or None if any required fields are missing.
    """
    original_case_name = family_data.get("title", {}).get("rendered")
    core_object = family_data.get("acf", {}).get("ccl_core_object")
    status = get_latest_document_status(family_data)
    case_number = family_data.get("acf", {}).get("ccl_case_number")

    empty_values = return_empty_values(
        [
            ("core_object", core_object),
            ("status", status),
            ("case_number", case_number),
        ]
    )

    if empty_values:
        click.echo(
            f"🛑 Skipping US case ({case_id}), missing family metadata: {', '.join(empty_values)}"
        )
        return None

    family_metadata = {
        "original_case_name": [original_case_name] if original_case_name else [],
        "id": [str(case_id)],
        "status": [status],
        "case_number": [case_number],
        "core_object": [core_object],
    }

    return family_metadata


def process_us_case_data(
    family_data: dict[str, Any], case_id: int, context: LitigationContext
) -> Optional[dict[str, Any]]:
    """
    Maps the data of a US case to the internal family structure.

    :param dict[str, Any] family_data: The family data containing the case information.
    :param int case_id: The ID of the case.
    :param LitigationContext context: The context of the litigation project import.

    :return Optional[dict[str, Any]]: The mapped family data, or None if any required fields are missing.
    """
    family_metadata = process_us_case_metadata(family_data, case_id)
    title = family_data.get("title", {}).get("rendered")
    bundle_ids = family_data.get("acf", {}).get("ccl_case_bundle", [])
    state_code = family_data.get("acf", {}).get("ccl_state")
    geographies = ["USA"]

    empty_values = return_empty_values(
        [("title", title), ("bundle_ids", bundle_ids), ("ccl_state", state_code)]
    )

    if empty_values:
        click.echo(
            f"🛑 Skipping US case ({case_id}), missing {', '.join(empty_values)}"
        )
        return None

    if any(id not in context.case_bundles for id in bundle_ids):
        click.echo(
            f"🛑 Skipping US case ({case_id}) as it does not have a valid case bundle"
        )
        return None

    collections = [f"Sabin.collection.{id}.0" for id in bundle_ids]
    description = context.case_bundles[bundle_ids[0]]["description"]

    state_iso_code = to_us_state_iso(state_code)

    if state_iso_code:
        geographies.append(state_iso_code)
    else:
        click.echo(
            f"🛑 Skipping US case ({case_id}) as it does not have a ccl state code: {state_code}"
        )
        return None

    if not family_metadata:
        return None

    us_family = {
        "import_id": f"Sabin.family.{case_id}.0",
        "title": title,
        "summary": description if description else " ",
        "geographies": geographies,
        "metadata": family_metadata,
        "collections": collections,
        "category": "Litigation",
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

    :param dict[str, Any] family: A dictionary containing family data, which includes jurisdiction IDs.
    :param dict[str, dict[str, str]] mapped_jurisdictions: A dictionary mapping jurisdiction IDs to their ISO codes.
    :return list[str] : A list of ISO codes for the jurisdictions, or a default value if none are found.
    """

    # International : XAA

    jurisdiction_ids = family.get("jurisdiction", [])
    iso_codes = []

    for jurisdiction_id in jurisdiction_ids:
        if jurisdiction_id in mapped_jurisdictions:
            iso_codes.append(mapped_jurisdictions[jurisdiction_id]["iso"])

    return iso_codes if iso_codes else ["XAA"]


def map_families(
    families_data: dict[str, Any], context: LitigationContext
) -> list[dict[str, Any]]:
    """Maps the litigation case information to the internal data structure.

    This function transforms family data, which the Sabin Centre refers to as
    cases, into our internal data modelling structure. It returns a list of
    mapped families, each represented as a dictionary matching the required schema.

    :parm dict[str, Any] families_data: The case related data, structured as global cases,
        us cases and information related to global jurisdictions.
    :param LitigationContext context: The context of the litigation project import.
    :return list[dict[str, Any]]: A list of litigation families in
        the 'destination' format described in the Litigation Data Mapper Google
        Sheet.
    """
    if context.debug:
        click.echo("📝 No Litigation family data to wrangle.")

    global_cases = families_data.get("global_cases", [])
    us_cases = families_data.get("us_cases", [])
    jurisdictions = families_data.get("jurisdictions", [])

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

    mapped_jurisdictions = map_global_jurisdictions(jurisdictions)

    mapped_families = []

    for index, data in enumerate(us_cases):
        case_id = data.get("id")
        if not case_id:
            click.echo(
                f"🛑 Skipping US case at index: {index} as it does not contain a case id"
            )
            continue

        result = process_us_case_data(data, case_id, context)

        if result:
            mapped_families.append(result)
        else:
            context.skipped_families.append(case_id)

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
        else:
            context.skipped_families.append(case_id)
    return mapped_families
