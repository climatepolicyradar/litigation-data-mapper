from datetime import datetime
from typing import Any, Dict, cast

import click

from litigation_data_mapper.datatypes import LitigationContext
from litigation_data_mapper.parsers.utils import get_jurisdiction_iso


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
    global_jurisdictions: list[dict[str, str | int]],
) -> dict[str, dict[str, str]]:
    """
    Map global jurisdictions to their corresponding country names and ISO codes.

    This function takes a list of global jurisdictions, extracts the country name
    from each jurisdiction, checks that it is a valid country, and maps it to its corresponding
    ISO code if its not none. The result is a dictionary where the keys are jurisdiction IDs
    and the values are dictionaries containing the jurisdiction name and ISO code.

    :param list[dict[str, str]] global_jurisdictions: A list of dictionaries representing
        global jurisdictions, each containing 'id' and 'name' fields.
    :return dict[str, dict[str, str]]: A dictionary mapping jurisdiction IDs to their
        corresponding names and ISO codes.
    """
    mapped_jurisdictions = {}

    for jurisdiction in global_jurisdictions:
        jurisdiction_iso = get_jurisdiction_iso(
            cast(str, jurisdiction["name"]), cast(int, jurisdiction["parent"])
        )
        if jurisdiction_iso:
            mapped_jurisdictions[jurisdiction["id"]] = {
                "name": jurisdiction["name"],
                "iso": jurisdiction_iso,
            }

    return mapped_jurisdictions


def return_empty_values(data: list[tuple]) -> list[str]:
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

    return empty_fields


def initialise_counter(counter: dict[str, int], key: str) -> None:
    """Initialises the counter for a given key if not present.
    :param counter: A dictionary containing unique keys and their associated counts.
    :param key: The key to initialize a counter for.
    """
    if key not in counter:
        counter[key] = 0


def write_error_log(
    context: LitigationContext, output_path: str = "error_log.txt"
) -> None:
    """Writes the failures, skipped documents, and skipped families to a readable error log file.

    :param LitigationContext context: The context containing failures and skipped items
    :param str output_path: Path to the output error log file
    """
    with open(output_path, "w") as f:
        f.write("=== LITIGATION DATA MAPPER ERROR LOG ===\n\n")

        # Write failures
        f.write("FAILURES:\n")
        f.write("-" * 80 + "\n")
        if context.failures:
            for i, failure in enumerate(context.failures, 1):
                f.write(f"Failure #{i}:\n")
                f.write(f"  ID: {failure.id}\n")
                f.write(f"  Type: {failure.type}\n")
                f.write(f"  Reason: {failure.reason}\n")
                f.write("-" * 80 + "\n")
        else:
            f.write("No failures recorded.\n")
            f.write("-" * 80 + "\n")

        # Write skipped documents
        f.write("\nSKIPPED DOCUMENTS:\n")
        f.write("-" * 80 + "\n")
        if context.skipped_documents:
            for i, doc_id in enumerate(context.skipped_documents, 1):
                f.write(f"#{i}: Document ID {doc_id}\n")
        else:
            f.write("No documents were skipped.\n")
        f.write("-" * 80 + "\n")

        # Write skipped families
        f.write("\nSKIPPED FAMILIES/CASES:\n")
        f.write("-" * 80 + "\n")
        if context.skipped_families:
            for i, family_id in enumerate(context.skipped_families, 1):
                f.write(f"#{i}: Family/Case ID {family_id}\n")
        else:
            f.write("No families/cases were skipped.\n")
        f.write("-" * 80 + "\n")

        # Write summary
        f.write("\nSUMMARY:\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total failures: {len(context.failures)}\n")
        f.write(f"Total skipped documents: {len(context.skipped_documents)}\n")
        f.write(f"Total skipped families/cases: {len(context.skipped_families)}\n")

    if context.debug:
        click.echo(f"📝 Error log written to {output_path}")


def sort_documents_by_file_id(list_of_docs: list[dict], case_type: str) -> list[dict]:
    """Sorts a list of documents by their file ID in ascending order. Handles empty or missing file IDs.

    :param list[dict] list_of_docs: The list of documents to sort.
    :param str case_type: The type of case, either 'case' or 'non-case'.
    :return list[dict]: The sorted list of documents.
    """
    document_id_key = "ccl_file" if case_type == "case" else "ccl_nonus_file"
    return sorted(list_of_docs, key=lambda doc: doc.get(document_id_key) or 0)
