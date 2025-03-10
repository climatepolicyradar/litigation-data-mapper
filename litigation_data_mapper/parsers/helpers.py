from datetime import datetime
from typing import Any, Dict

import click

from litigation_data_mapper.parsers.utils import to_country, to_iso


def _get_nested_keys(d: Dict[str, Any], parent_key: str = "") -> set:
    """
    Retrieve all keys from a dictionary, including nested keys, as dot-separated paths,
    while excluding specific fields.

    This function recursively traverses through the dictionary, including nested dictionaries,
    to generate a set of keys represented as dot-separated paths (e.g., 'parent.child').
    Additionally, it allows certain fields to be excluded from the key set.

    :param Dict[str, Any] d: The dictionary from which to extract keys.
    :param str parent_key: A string used to accumulate the key path during recursion.
                        It should be empty for the initial call.
    :return set : A set of strings representing all keys (including nested keys)
             as dot-separated paths, excluding the specified `excluded_fields`.
    """

    # Exclude word press related keys
    excluded_keys = ["yoast_head_json", "_links", "yoast_head"]

    keys = set()
    for key, value in d.items():
        if key in excluded_keys:
            continue

        keys.add(key)
        if isinstance(value, dict):
            keys.update(_get_nested_keys(value))
    return keys


def verify_required_fields_present(
    data: dict[str, Any], required_fields: set[str]
) -> bool:
    """Verify that the required fields are present in the data.

    :param dict[str, Any] data: The data to check.
    :param set[str] required_fields: The required data fields.
    :raise AttributeError if any of the required fields are missing.
    :return bool: True if the data contains the required fields.
    """
    data_keys = _get_nested_keys(data)
    diff = set(required_fields).difference(data_keys)
    if diff == set():
        return True

    # sets are naturally un-ordered,
    # sorting them means we can test the error message reliably
    sorted_diff = sorted(diff)
    sorted_cols = sorted(data_keys)

    raise AttributeError(
        f"Required fields {sorted_diff} not present in data: {sorted_cols}"
    )


def parse_document_filing_date(doc: dict) -> datetime:
    """
    Parse the document's filing date from the 'ccl_filing_date' field.

    This function retrieves the filing date from the provided document dictionary,
    expecting the date to be in the 'YYYYMMDD' format. If the filing date is not
    present or is empty, it returns the minimum datetime value.

    :param dict doc: The document dictionary containing the 'ccl_filing_date'.
    :return datetime: The parsed filing date as a datetime object, or datetime.min
                      if the filing date is missing.
    """
    # Define a date format that matches the 'YYYYMMDD' format of 'ccl_filing_date'
    date_format = "%Y%m%d"

    filing_date_str = doc.get("ccl_filing_date", "")
    if filing_date_str:
        return datetime.strptime(filing_date_str, date_format)
    return (
        datetime.min
    )  # gracefully handle instances where there is a missing filing date in the document


def map_global_jurisdictions(
    global_jurisdictions: list[dict[str, str]],
) -> dict[str, dict[str, str]]:
    """
    Map global jurisdictions to their corresponding country names and ISO codes.

    This function takes a list of global jurisdictions, extracts the country name
    from each jurisdiction, checks that it is a valid country, and maps it to its corresponding ISO code if its not none. The result is a dictionary where the keys are jurisdiction IDs and the values are dictionaries containing the jurisdiction name and ISO code.

    :param list[dict[str, str]] global_jurisdictions: A list of dictionaries representing
                                                      global jurisdictions, each containing
                                                      'id' and 'name' fields.
    :return dict[str, dict[str, str]]: A dictionary mapping jurisdiction IDs to their
                                         corresponding names and ISO codes.
    """
    mapped_jurisdictions = {}

    for jurisdiction in global_jurisdictions:
        # Get country name from jurisdiction name
        country = to_country(jurisdiction["name"])

        if country is not None:
            jurisdiction_id = jurisdiction["id"]
            mapped_jurisdictions[jurisdiction_id] = {
                "name": jurisdiction["name"],
                "iso": to_iso(country),
            }

    return mapped_jurisdictions


def contains_empty_values(data: list[tuple]) -> bool:
    """Check if the data contains any empty values.

    This function checks if the data contains any empty values. It returns True
    if any of the values are empty, and False otherwise.

    :param list[tuple] data: The data to check.
    :return bool: True if the data contains empty values, False otherwise.
    """
    empty_fields = []

    for name, value in data:
        if not value:
            empty_fields.append(name)

    if empty_fields:
        click.echo(
            f"🛑 Skipping family litigation; missing the following fields: {', '.join(empty_fields)}"
        )

    return False
