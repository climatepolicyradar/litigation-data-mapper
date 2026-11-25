from functools import lru_cache
from typing import Any

import click
import requests
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from urllib3.util import Retry

from litigation_data_mapper.utils import get_ssm_parameter

PARAMETER_WORDPRESS_USER_NAME = "/Litigation/WordPress/User"
PARAMETER_WORDPRESS_APP_PASSWORD_NAME = (
    "/Litigation/WordPress/AppPassword"  # nosec: B105
)


@lru_cache(maxsize=1)
def get_wordpress_credentials() -> tuple[str, str]:
    """Get the WordPress API credentials from AWS SSM Parameter Store.

    Cached as a session is created for every request made to WordPress.

    :return tuple[str, str]: The WordPress user and application password.
    """
    return (
        get_ssm_parameter(PARAMETER_WORDPRESS_USER_NAME),
        get_ssm_parameter(PARAMETER_WORDPRESS_APP_PASSWORD_NAME),
    )


def create_retry_session(
    retries: int = 5, backoff_factor: float = 5
) -> requests.Session:
    """Create a requests session with automatic retries.

    :param int retries: Number of retry attempts before failing.
    :param float backoff_factor: Delay multiplier for exponential backoff.
    :return requests.Session: A requests session with retry handling.
    """
    wp_user, wp_app_password = get_wordpress_credentials()

    session = requests.Session()
    session.auth = HTTPBasicAuth(wp_user, wp_app_password)

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
            raise

    click.echo("✅ Completed fetching from endpoint.")
    return all_data


class IncompleteWordPressFetchError(RuntimeError):
    """Raised when we could not retrieve every item WordPress says exists."""


def fetch_word_press_concepts(
    endpoint: str, per_page: int = 100
) -> list[dict[str, Any]]:
    """Fetch every concept in a WordPress taxonomy using an "exclude walk".

    (WordPress calls these "taxonomy terms".) WordPress ignores `orderby` on
    taxonomy endpoints, so paging through them with `page=N` returns some concepts
    twice and silently skips others (which concepts are skipped changes between
    runs). Post endpoints are not affected.

    Instead we keep requesting the first page while excluding every concept id we have
    already seen, until WordPress returns an empty page. Each request can only
    return concepts we have not seen yet, so ordering no longer matters.

    :param str endpoint: The taxonomy URL, e.g. `.../wp-json/wp/v2/jurisdiction`.
    :param int per_page: Number of concepts per request (WordPress max is 100).
    :raises IncompleteWordPressFetchError: If fewer concepts are returned than the
        `X-WP-Total` header says exist, or if WordPress ignores `exclude`.
    :return list[dict[str, Any]]: Every concept in the taxonomy.
    """
    session = create_retry_session()
    concepts: dict[int, dict[str, Any]] = {}
    expected_total: int | None = None

    click.echo(f"⏳ Fetching all concepts from {endpoint}...")

    while True:
        query = f"per_page={per_page}"
        if concepts:
            # Built by hand so the commas are not percent-encoded, which keeps the
            # URL short (~5KB for our largest taxonomy rather than ~7KB).
            query += "&exclude=" + ",".join(str(concept_id) for concept_id in concepts)

        try:
            with session.get(f"{endpoint}?{query}", timeout=30) as response:
                response.raise_for_status()
                if expected_total is None and "X-WP-Total" in response.headers:
                    expected_total = int(response.headers["X-WP-Total"])
                batch: list[dict[str, Any]] = response.json()
        except requests.RequestException as e:
            click.echo(f"❌ Error fetching concepts from {endpoint}: {e}", err=True)
            raise

        if not batch:
            break

        new_concepts = [concept for concept in batch if concept["id"] not in concepts]
        if not new_concepts:
            raise IncompleteWordPressFetchError(
                f"{endpoint} returned only concepts we had already seen; "
                "WordPress appears to be ignoring the `exclude` parameter."
            )
        for concept in new_concepts:
            concepts[concept["id"]] = concept

    if expected_total is not None and len(concepts) < expected_total:
        raise IncompleteWordPressFetchError(
            f"Fetched {len(concepts)} concepts from {endpoint} but WordPress reports "
            f"{expected_total}."
        )

    click.echo(f"✅ Fetched {len(concepts)} concepts from {endpoint}.")
    return list(concepts.values())


def fetch_individual_wordpress_resource(endpoint: str) -> dict[str, Any]:
    """Fetch a single WordPress resource.

    :raises requests.RequestException: If the resource could not be fetched, so the
        caller can record why.
    """
    session = create_retry_session()
    click.echo(f"⏳ fetching individual resource from {endpoint}...")
    try:
        response = session.get(endpoint, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        click.echo(
            f"❌ Error fetching individual resource from {endpoint}: {e}", err=True
        )
        raise
