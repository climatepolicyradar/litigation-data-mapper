from typing import Any, TypedDict

import click

from litigation_data_mapper.extract_concepts import Concept, extract_concepts
from litigation_data_mapper.wordpress import fetch_word_press_data

ENDPOINTS = {
    "case_bundles": "https://climatecasechart.com/wp-json/wp/v2/case_bundle",
    "document_media": "https://climatecasechart.com/wp-json/wp/v2/media",
    "global_cases": "https://climatecasechart.com/wp-json/wp/v2/non_us_case",
    "jurisdictions": "https://climatecasechart.com/wp-json/wp/v2/jurisdiction",
    "us_cases": "https://climatecasechart.com/wp-json/wp/v2/case",
}


class LitigationType(TypedDict):
    collections: list[dict[str, Any]]
    families: dict[str, list[dict[str, Any]]]
    documents: list[dict[str, Any]]
    concepts: dict[int, Concept]


def fetch_litigation_data() -> LitigationType:
    """Fetch litigation data from WordPress API endpoints.

    :return Litigation: A dictionary containing collections, families, documents, and events.
    """
    click.echo("⏳ Fetching litigation data from WordPress endpoints...")

    collections_data = fetch_word_press_data(ENDPOINTS["case_bundles"])
    us_cases_data = fetch_word_press_data(ENDPOINTS["us_cases"])
    global_cases_data = fetch_word_press_data(ENDPOINTS["global_cases"])
    jurisdictions_data = fetch_word_press_data(ENDPOINTS["jurisdictions"])
    document_media = fetch_word_press_data(ENDPOINTS["document_media"])

    litigation_data: LitigationType = {
        "collections": collections_data,
        "families": {
            "us_cases": us_cases_data,
            "global_cases": global_cases_data,
            "jurisdictions": jurisdictions_data,
        },
        "documents": document_media,
        "concepts": extract_concepts(),
    }

    click.echo("✅ Completed fetching litigation data.")
    return litigation_data
