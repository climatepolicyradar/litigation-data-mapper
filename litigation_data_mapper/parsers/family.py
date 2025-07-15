from typing import Any

import click

from litigation_data_mapper.datatypes import Failure, LitigationContext
from litigation_data_mapper.extract_concepts import Concept
from litigation_data_mapper.extract_concepts import taxonomies as concept_taxonomies
from litigation_data_mapper.parsers.helpers import (
    map_global_jurisdictions,
    parse_document_filing_date,
    return_empty_values,
)
from litigation_data_mapper.parsers.utils import last_modified_date, to_us_state_iso

NO_US_STATE_CODE = "XX"  # Default code for federal cases without a state code


def process_global_case_metadata(
    family_data: dict[str, Any], case_id: int, concepts: list[dict[str, Any]]
) -> dict[str, Any] | Failure:
    """
    Maps the metadata of a global case to the internal family metadata structure.

    :param dict family_data: The family data containing the case metadata.
    :param int case_id: The ID of the case.
    :return dict[str, Any] | Failure: The mapped family metadata, or None if any required fields are missing.
    """

    original_case_name = family_data.get("acf", {}).get("ccl_nonus_case_name")
    core_object = family_data.get("acf", {}).get("ccl_nonus_core_object")
    status = family_data.get("acf", {}).get("ccl_nonus_status")
    case_number = family_data.get("acf", {}).get("ccl_nonus_reporter_info")

    empty_values = return_empty_values(
        [
            ("core_object", core_object),
            ("status", status),
        ]
    )

    if empty_values:
        return Failure(
            id=case_id,
            type="non_us_case",
            reason=f"Missing the following values: {', '.join(empty_values)}",
        )

    concepts_metadata = [concept.get("preferred_label") for concept in concepts]

    family_metadata = {
        "original_case_name": [original_case_name] if original_case_name else [],
        "id": [str(case_id)],
        "status": [status],
        "case_number": [case_number] if case_number else [],
        "core_object": [core_object],
        "concept_preferred_label": concepts_metadata,
    }

    return family_metadata


def process_global_case_data(
    family_data: dict[str, Any],
    geographies: list[str],
    case_id: int,
    concepts: dict[int, Concept],
) -> dict[str, Any] | Failure:
    """
    Maps the data of a global case to the internal family structure.

    :param dict[str, Any] family_data: The family data containing the case information.
    :param list[str] geographies: The ISO codes of the geographies associated with the case.
    :param int case_id: The ID of the case.

    :return dict[str, Any] | Failure: The mapped family data, or None if any required fields are missing.
    """

    # Concepts
    family_concepts = get_concepts(family_data, concepts)

    family_metadata = process_global_case_metadata(
        family_data, case_id, family_concepts
    )

    title = family_data.get("title", {}).get("rendered")
    summary = family_data.get("acf", {}).get("ccl_nonus_summary")

    empty_values = return_empty_values([("title", title), ("summary", summary)])

    if empty_values:
        return Failure(
            id=case_id,
            type="non_us_case",
            reason=f"Missing the following values: {', '.join(empty_values)}",
        )

    if isinstance(family_metadata, Failure):
        return family_metadata

    global_family = {
        "import_id": f"Sabin.family.{case_id}.0",
        "title": title,
        "summary": summary,
        "geographies": sorted(geographies),
        "metadata": family_metadata,
        "category": "Litigation",
        "collections": [],
        "concepts": family_concepts,
    }

    return global_family


def get_latest_document_status(family: dict[str, Any]) -> str:
    """
    Retrieve the status of the latest document in the case, based on the filing date.

    This function retrieves a list of documents from the given case and determines which
    document has the most recent filing date by. If no documents are found, it returns None.

    :param dict[str, Any] family: The family dictionary containing document information.
    :return str: The status of the latest document (from the 'ccl_outcome' field),
                 or a generic response if no documents are found.
    """

    documents = family.get("acf", {}).get("ccl_case_documents", [])

    if not documents:
        return "Status Pending"  # Default status if no documents are found

    latest_document_in_case = max(
        documents, key=lambda doc: parse_document_filing_date(doc)
    )

    latest_outcome = latest_document_in_case.get("ccl_outcome")

    return latest_outcome if latest_outcome else "Status Pending"


def process_us_case_metadata(
    family_data: dict[str, Any], case_id: int, concepts: list[dict[str, Any]]
) -> dict[str, Any] | Failure:
    """
    Maps the metadata of a US case to the internal family metadata structure.

    :param dict[str, Any] family_data: The family data containing the case metadata.
    :param int case_id: The ID of the case.
    :return dict[str, Any] | Failure: The mapped family metadata, or Failure if any required fields are missing.
    """
    docket_number = family_data.get("acf", {}).get("ccl_docket_number")
    status = get_latest_document_status(family_data)

    empty_values = return_empty_values([("docket_number", docket_number)])

    if empty_values:
        return Failure(
            id=case_id,
            type="us_case",
            reason=f"Missing the following values: {', '.join(empty_values)}",
        )

    concepts_metadata = [concept.get("preferred_label") for concept in concepts]

    family_metadata = {
        "original_case_name": [],
        "id": [str(case_id)],
        "status": [status],
        "case_number": [docket_number],
        "core_object": [],
        "concept_preferred_label": concepts_metadata,
    }

    return family_metadata


def process_us_case_data(
    family_data: dict[str, Any],
    case_id: int,
    context: LitigationContext,
    concepts: dict[int, Concept],
    collections: list[dict[str, Any]],
) -> dict[str, Any] | Failure:
    """
    Maps the data of a US case to the internal family structure.

    :param dict[str, Any] family_data: The family data containing the case information.
    :param int case_id: The ID of the case.
    :param LitigationContext context: The context of the litigation project import.

    :return dict[str, Any] | Failure: The mapped family data, or Failure if any required fields are missing.
    """

    title = family_data.get("title", {}).get("rendered")
    bundle_ids: list[int] = family_data.get("acf", {}).get("ccl_case_bundle", [])
    state_code = family_data.get("acf", {}).get("ccl_state")
    geographies = ["USA"]

    # Concepts
    # concepts are stored on the case bundle in US cases, so we need to
    # - calculate which bundles are associated with the case
    # - read the concepts from that bundle
    # - associate those concepts with the case AKA family
    bundles = []
    for bundle_id in bundle_ids:
        matched_bundle = next(
            (collection for collection in collections if collection["id"] == bundle_id),
            None,
        )
        if matched_bundle:
            bundles.append(matched_bundle)

    family_concepts = []
    for bundle in bundles:
        family_concepts += get_concepts(bundle, concepts)
    # /Concepts

    family_metadata = process_us_case_metadata(family_data, case_id, family_concepts)

    empty_values = return_empty_values(
        [("title", title), ("bundle_ids", bundle_ids), ("ccl_state", state_code)]
    )

    if empty_values:
        return Failure(
            id=case_id,
            type="us_case",
            reason=f"Missing the following values: {', '.join(empty_values)}",
        )

    if any(id not in context.case_bundles for id in bundle_ids):
        return Failure(
            id=case_id, type="us_case", reason="Does not have a valid case bundle"
        )

    collection_ids = [f"Sabin.collection.{id}.0" for id in bundle_ids]

    description = context.case_bundles[bundle_ids[0]][
        "description"
    ]  # TODO: confirm with product this is the right approach and if this should be more intuitive

    if state_code != NO_US_STATE_CODE:
        state_iso_code = to_us_state_iso(state_code)

        if state_iso_code:
            geographies.append(state_iso_code)
        else:
            return Failure(
                id=case_id,
                type="us_case",
                reason=f"Does not have a valid ccl state code ({state_code})",
            )

    if isinstance(family_metadata, Failure):
        return family_metadata

    us_family = {
        "import_id": f"Sabin.family.{case_id}.0",
        "title": title,
        "summary": description if description else " ",
        "geographies": geographies,
        "metadata": family_metadata,
        "collections": collection_ids,
        "category": "Litigation",
        "concepts": family_concepts,
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


def validate_data(
    global_cases: list[dict[str, Any]],
    us_cases: list[dict[str, Any]],
    jurisdictions: list[dict[str, Any]],
) -> bool:
    """Validate that all required datasets are present.
    :param list[dict[str, Any]] global_cases: A list of global case data dictionaries.
    :param list[dict[str, Any]] us_cases: A list of US case data dictionaries.
    :param list[dict[str, Any]] jurisdictions: A list of jurisdiction data dictionaries.
    :return bool: True if all required datasets are present, otherwise False.
    """

    if not global_cases or not us_cases:
        missing_dataset = "global" if not global_cases else "US"
        click.echo(
            f"🛑 No {missing_dataset} cases found in the data. Skipping family litigation."
        )
        return False

    if not jurisdictions:
        click.echo(
            "🛑 No jurisdictions provided in the data. Skipping family litigation."
        )
        return False

    return True


def required_fields_present(
    data: dict[str, Any], context: LitigationContext, index: int
) -> bool:
    """
    Validates that the family data object has the required fields.

    :param dict[str, Any] data: The family data object to be validated.
    :param LitigationContext context: The context of the litigation project import.
    :param int index: The index of the family data object.
    :return bool: True if all required fields are present, False if any of the fields is missing.
    """
    case_id = data.get("id")
    if not isinstance(case_id, int):
        context.failures.append(
            Failure(
                id=None,
                type="case",
                reason=f"Does not contain a us case id at index ({index}).",
            )
        )
        return False
    if not data.get("modified_gmt"):
        context.skipped_families.append(case_id)
        context.failures.append(
            Failure(
                id=case_id,
                type="case",
                reason="Does not contain a modified_gmt timestamp.",
            )
        )
        return False

    return True


def map_families(
    families_data: dict[str, Any],
    context: LitigationContext,
    collections: list[dict[str, Any]],
    concepts: dict[int, Concept],
) -> list[dict[str, Any]]:
    """Maps the litigation case information to the internal data structure.

    This function transforms family data, which the Sabin Centre refers to as
    cases, into our internal data modelling structure. It returns a list of
    mapped families, each represented as a dictionary matching the required schema.

    :parm dict[str, Any] families_data: The case related data, structured as global cases,
        us cases and information related to global jurisdictions.
    :param LitigationContext context: The context of the litigation project import.
    :param dict[int, Concept] | None concepts: Optional dictionary mapping concept IDs to Concept objects.
    :return list[dict[str, Any]]: A list of litigation families in
        the 'destination' format described in the Litigation Data Mapper Google
        Sheet.
    """
    if context.debug:
        click.echo("📝 Wrangling litigation family data.")

    failure_count = len(context.failures)

    concepts = concepts or {}

    global_cases = families_data.get("global_cases", [])
    us_cases = families_data.get("us_cases", [])
    jurisdictions = families_data.get("jurisdictions", [])

    if not validate_data(global_cases, us_cases, jurisdictions):
        return []

    mapped_jurisdictions = map_global_jurisdictions(jurisdictions)

    mapped_families = []

    # Process US Cases
    for index, data in enumerate(us_cases):
        if not required_fields_present(data, context, index):
            continue

        case_id = data.get("id")

        should_process = (
            not context.get_modified_data
            or last_modified_date(data) > context.last_import_date
        )

        if should_process:
            result = process_us_case_data(
                data, case_id, context, concepts=concepts, collections=collections
            )

            if isinstance(result, Failure):
                context.failures.append(result)
                context.skipped_families.append(case_id)
            else:
                mapped_families.append(result)
        else:
            context.skipped_families.append(case_id)

    # Process Global cases
    for index, data in enumerate(global_cases):
        if not required_fields_present(data, context, index):
            continue

        case_id = data.get("id")

        should_process = (
            not context.get_modified_data
            or last_modified_date(data) > context.last_import_date
        )

        if should_process:
            geographies = get_jurisdiction_iso_codes(data, mapped_jurisdictions)
            result = process_global_case_data(
                data, geographies, case_id, concepts=concepts
            )
            if isinstance(result, Failure):
                context.failures.append(result)
                context.skipped_families.append(case_id)
            else:
                mapped_families.append(result)
        else:
            context.skipped_families.append(case_id)

    if len(context.failures) > failure_count:
        click.echo(
            "🛑 Some families have been skipped during the mapping process, related events and documents will not be mapped, check the failures log."
        )

    return mapped_families


def get_concepts(
    case: dict[str, Any], concepts: dict[int, Concept]
) -> list[dict[str, Any]]:
    click.echo(f"📝 Mapping concepts for family: {case.get('id')}")

    family_concepts = []

    for taxonomy in concept_taxonomies:
        concept_ids = case.get(taxonomy, [])
        for concept_id in concept_ids:
            concept = concepts.get(concept_id)
            if concept is None:
                click.echo(
                    f"🛑 Concept {concept_id} not found in concepts {case['id']}"
                )
            else:
                family_concepts.append(
                    {
                        "id": concept.id,
                        "ids": [],
                        "type": concept.type.value,
                        "preferred_label": concept.preferred_label,
                        "relation": concept.relation,
                        "subconcept_of_labels": concept.subconcept_of_labels,
                    }
                )

    return family_concepts
