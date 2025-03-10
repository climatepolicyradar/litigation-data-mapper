from typing import Optional

import click
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

ENDPOINTS = {
    "case_bundles": "https://climatecasechart.com/wp-json/wp/v2/case_bundle",
    "document_media": "https://climatecasechart.com/wp-json/wp/v2/media",
    "global_cases": "https://climatecasechart.com/wp-json/wp/v2/non_us_case",
    "jurisdictions": "https://climatecasechart.com/wp-json/wp/v2/jurisdiction",
    "us_cases": "https://climatecasechart.com/wp-json/wp/v2/case",
}


def create_retry_session(
    retries: int = 3, backoff_factor: float = 1.5
) -> requests.Session:
    """Create a requests session with automatic retries.

    :param int retries: Number of retry attempts before failing.
    :param float backoff_factor: Delay multiplier for exponential backoff.
    :return requests.Session: A requests session with retry handling.
    """
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    return session


def fetch_word_press_data(endpoint: str, per_page: int = 100) -> Optional[list[dict]]:
    """Fetch paginated data from a given API endpoint.

    :param str endpoint: The API URL to fetch data from.
    :param int per_page: Number of results per page (default: 100).
    :return Optional[list[dict]]: A list of data records if successful, or None if an error occurs.
    """
    all_data = []
    page = 1
    total_pages = 1

    session = create_retry_session()

    click.echo(f"⏳ {endpoint}...")

    while page <= total_pages:
        try:
            response = session.get(
                endpoint,
                params={"page": page, "per_page": per_page},
                timeout=10,
            )
            response.raise_for_status()
            if page == 1:
                # We know that the word press endpoint provides details of the total
                # pages in the headers, when iterating we will handle instances where this
                # value does not exist
                total_pages = int(response.headers.get("X-WP-TotalPages", 1))

            data = response.json()
            if not data:
                break
            all_data.extend(data)
            page += 1
        except requests.RequestException as e:
            click.echo(f"❌ Error fetching data from {endpoint}: {e}", err=True)
            return None
    return all_data


def fetch_litigation_data() -> dict[str, list[dict]]:
    """Fetch litigation data from WordPress API endpoints.

    :param bool debug: Whether to print debug messages.
    :return dict[str, list[dict]]: A dictionary containing collections, families, documents, and events.
    """
    click.echo("⏳ Fetching litigation data from WordPress endpoints...")

    collections_data = fetch_word_press_data(ENDPOINTS["case_bundles"])
    us_cases_data = fetch_word_press_data(ENDPOINTS["us_cases"])
    global_cases_data = fetch_word_press_data(ENDPOINTS["global_cases"])
    jurisdictions_data = fetch_word_press_data(ENDPOINTS["jurisdictions"])

    litigation_data = {
        "collections": collections_data,
        "families": [
            {
                "us_cases": us_cases_data,
                "global_cases": global_cases_data,
                "jurisdictions": jurisdictions_data,
            }
        ],
        "documents": [],
        "events": [],
    }

    click.echo("✅ Completed fetching litigation data.")
    return litigation_data
