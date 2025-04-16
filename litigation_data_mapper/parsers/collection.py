import html
from typing import Any

import click

from litigation_data_mapper.datatypes import Failure, LitigationContext
from litigation_data_mapper.enums.collections import RequiredCollectionKeys
from litigation_data_mapper.parsers.helpers import verify_required_fields_present
from litigation_data_mapper.parsers.utils import last_import_date, last_modified_date


def process_collection_data(
    data: dict[str, Any], index: int, bundle_id: int | None
) -> dict[str, Any] | Failure:
    """Process the case bundle data and return it in a structured format.

    :param data: The raw data for the collection, expected to be a dictionary containing
                 information like title and description.
    :param index: The index of the current case bundle in the collection, used for logging purposes.
    :param bundle_id: The unique identifier for the case bundle. If it's not present,
                       the case bundle will be skipped.
    :return: A dictionary containing the processed collection data, or Failure if the data is incomplete.
    """
    if not isinstance(bundle_id, int):
        return Failure(
            id=None,
            type="case_bundle",
            reason=f"Does not contain a bundle id at index ({index})",
        )

    collection_id = bundle_id
    import_id = f"Sabin.collection.{collection_id}.0"

    description = data.get("acf", {}).get("ccl_core_object")
    title = data.get("title", {}).get("rendered")

    if not description or not title:
        return Failure(
            id=bundle_id,
            type="case_bundle",
            reason=f"Does not contain {'a description' if not description else 'a title'}",
        )

    collection_data = {
        "import_id": import_id,
        "description": description,
        "title": html.unescape(title),
        "metadata": {"id": [str(bundle_id)]},
    }
    return collection_data


def map_collections(
    collections_data: list[dict[str, Any]], context: LitigationContext
) -> list[dict[str, Any]]:
    """Map the Litigation collection information to the internal data structure.

    This function transforms litigation collection data, referred to as 'case bundles'
    by the Sabin Centre, into a format representing groups of families (cases) that
    share a common theme. It returns a list of mapped collections, each represented as a
    dictionary matching the required schema.

    :param LitigationContext context: The context of the litigation project import.
    :return list[Optional[dict[str, Any]]]: A list of litigation collections in
        the 'destination' format described in the Litigation Data Mapper Google
        Sheet.
    """
    if context.debug:
        click.echo("📝 Wrangling litigation collection data.")

    mapped_collections_data = []

    required_fields = {str(e.value) for e in RequiredCollectionKeys}

    for index, data in enumerate(collections_data):
        verify_required_fields_present(data, required_fields)
        bundle_id = data.get(RequiredCollectionKeys.BUNDLE_ID.value)

        if context.get_all_data or last_modified_date(data) > context.last_import_date:
            result = process_collection_data(data, index, bundle_id)

            if isinstance(result, Failure):
                context.failures.append(result)
            else:
                mapped_collections_data.append(result)
                if bundle_id:
                    context.case_bundles[bundle_id] = {
                        "description": result["description"]
                    }

    if context.failures:
        click.echo(
            "🛑 Some case bundles have been skipped during the mapping process, check the failures log."
        )
    return mapped_collections_data
