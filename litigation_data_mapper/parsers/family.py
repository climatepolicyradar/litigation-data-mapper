from typing import Any, Optional

import click

from litigation_data_mapper.parsers.helpers import map_global_jurisdictions


def process_global_case_data(family_data, geographies, case_id):
    pass


def process_us_case_metadata(family_data, case_id):
    pass


def process_us_case_data(family_data, case_id):
    pass


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
            "🛑 No global or US cases found in the data. Skipping family litigation."
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
