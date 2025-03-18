import html
from typing import Any, Optional

import click

from litigation_data_mapper.enums.collections import RequiredCollectionKeys
from litigation_data_mapper.parsers.helpers import verify_required_fields_present


def process_collection_data(
    data: dict[str, Any], index: int, bundle_id: Optional[str]
) -> Optional[dict[str, Any]]:
    """Process the case bundle data and return it in a structured format.

    :param data: The raw data for the collection, expected to be a dictionary containing
                 information like title and description.
    :param index: The index of the current case bundle in the collection, used for logging purposes.
    :param bundle_id: The unique identifier for the case bundle. If it's not present,
                       the case bundle will be skipped.
    :return: A dictionary containing the processed collection data, or None if the data is incomplete.
    """
    if not bundle_id:
        click.echo(
            f"🛑 Skipping case bundle at index: {index} as it does not contain a bundle id"
        )
        return None

    collection_id = bundle_id
    import_id = f"Litigation.collection.{collection_id}.0"

    description = data.get("acf", {}).get("ccl_core_object")
    title = data.get("title", {}).get("rendered")

    if description is None or title is None:
        click.echo(
            f"🛑 Error at bundle id : {bundle_id} - Empty values found for description and/or title. Skipping....."
        )
        return None

    collection_data = {
        "import_id": import_id,
        "description": description,
        "title": html.unescape(title),
        "metadata": {"id": [bundle_id]},
    }
    return collection_data


def map_collections(
    collections_data: list[dict[str, Any]], context: dict[str, Any]
) -> list[dict[str, Any]]:
    """Map the Litigation collection information to the internal data structure.

    This function transforms litigation collection data, referred to as 'case bundles'
    by the Sabin Centre, into a format representing groups of families (cases) that
    share a common theme. It returns a list of mapped collections, each represented as a
    dictionary matching the required schema.

    :param dict[str, Any]: The context of the litigation project import.
    :return list[Optional[dict[str, Any]]]: A list of litigation collections in
        the 'destination' format described in the Litigation Data Mapper Google
        Sheet.
    """
    if context["debug"]:
        click.echo("📝 Wrangling litigation collection data.")

    mapped_collections_data = []
    context["case_bundles"] = {}

    required_fields = {str(e.value) for e in RequiredCollectionKeys}

    for index, data in enumerate(collections_data):
        verify_required_fields_present(data, required_fields)
        bundle_id = data.get(RequiredCollectionKeys.BUNDLE_ID.value)
        result = process_collection_data(data, index, bundle_id)
        if result:
            mapped_collections_data.append(result)
            context["case_bundles"][bundle_id] = {"description": result["description"]}

    return mapped_collections_data
