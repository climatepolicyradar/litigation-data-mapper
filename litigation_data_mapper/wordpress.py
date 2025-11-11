import re
from typing import Any

import click
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


def create_retry_session(
    retries: int = 5, backoff_factor: float = 5
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


def fetch_word_press_data(endpoint: str, per_page: int = 100) -> list[dict[str, Any]]:
    """Fetch paginated data from a given API endpoint.

    :param str endpoint: The API URL to fetch data from.
    :param int per_page: Number of results per page (default: 100).
    :return Optional[list[dict]]: A list of data records if successful, or None if an error occurs.
    """
    all_data = []
    page = 1
    total_pages = 1

    session = create_retry_session()

    click.echo(f"⏳ fetching from {endpoint}...")

    while page <= total_pages:
        try:
            with session.get(
                endpoint,
                params={
                    "page": page,
                    "per_page": per_page,
                    "orderby": "id",
                    "order": "desc",
                },
                timeout=10,
            ) as response:
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
            return []

    click.echo("✅ Completed fetching from endpoint.")
    return all_data


def fetch_individual_wordpress_resource(endpoint: str) -> dict[str, Any] | None:
    session = create_retry_session()
    try:
        click.echo(f"⏳ fetching individual resource from {endpoint}...")
        response = session.get(endpoint, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        click.echo(
            f"❌ Error fetching individual resource from {endpoint}: {e}", err=True
        )
        return None
