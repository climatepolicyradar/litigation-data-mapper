from datetime import datetime

import pycountry
from pycountry.db import Country, Subdivision


def to_country(country: str | None) -> Country | None:
    """
    Convert a country name to a pycountry country object.

    :param str country: The name of the country.
    :return: A pycountry country object or None if not found.
    """

    if not country:
        return None

    try:
        country_obj = pycountry.countries.get(name=country)

        if country_obj:
            return country_obj

        # If not found, try to find the country using fuzzy search
        countries = pycountry.countries.search_fuzzy(country)

        return countries[0] if countries else None  # pyright: ignore

    except (AttributeError, LookupError):
        return None


def to_us_state_iso(state_code: str | None) -> str | None:
    """
    Retrieves the full ISO-3166-2 format code for a US state based on a two-letter state code.

    This function validates the state code and returns the corresponding ISO 3166-2 code
    if the state is valid, or None if not found.

    :param str|None state_code: A two-letter state code (e.g., 'CA', 'NY').
    :return: The ISO 3166-2 code for the US state (e.g., 'US-CA') or None if invalid.
    """

    if not state_code:
        return None

    try:
        us_country = pycountry.countries.get(alpha_3="USA")
        us_subdivisions = pycountry.subdivisions.get(
            country_code=us_country.alpha_2  # pyright: ignore
        )
    except (LookupError, AttributeError):
        return None

    if not us_subdivisions:
        return None

    state = next(
        (
            subdivision
            for subdivision in us_subdivisions
            if subdivision.code
            == f"{us_country.alpha_2}-{state_code}"  # pyright: ignore
        ),
        None,
    )

    return state.code if state else None


def to_country_subdivision(territory: str) -> Subdivision | None:
    """
    Convert a country subdivision name to a pycountry subdivision object.

    :param str subdivision: The name of the country subdivision.
    :return: A pycountry subdivision object or None if not found.
    """

    try:
        related_territories = pycountry.countries.search_fuzzy(territory)
    except LookupError:
        return None

    parent_territory = related_territories[0] if related_territories else None

    if not parent_territory:
        return None

    # Pyright raises - Cannot access attribute "alpha_2" for class "type[ExistingCountries]" Attribute "alpha_2" is unknown
    # when testing this is false as we get back the pycountry country object not Existing Countries class obj, so ignoring for now
    try:
        subdivision_hierarchies = pycountry.subdivisions.get(
            country_code=parent_territory.alpha_2  # pyright: ignore
        )
    except LookupError:
        return None

    if not subdivision_hierarchies:
        return None

    subdivision_hierarchy = next(
        (
            subdivision
            for subdivision in subdivision_hierarchies
            if subdivision.name == territory
        ),
        None,
    )

    return subdivision_hierarchy


def to_iso(country: Country) -> str:
    """
    Convert a pycountry country object to its ISO alpha-3 code.

    :param country: A pycountry country object.
    :return str: The ISO alpha-3 code of the country, or an empty string if the country is None.
    """
    return country.alpha_3


def get_jurisdiction_iso(jurisdiction: str, parent_id: int) -> str | None:
    """
    This function takes a jurisdiction name and returns the corresponding ISO code.
    ISO 3166-2 for subdivisions
    ISO 3166-1 alpha-3 for countries

    :param str jurisdiction: The name of the jurisdiction.
    :param int parent_id: The id of the the jurisdiction, parent id of 0 indicates that it's the parent jurisdiction.
    :return str: The ISO code of the jurisdiction, or None if the jurisdiction is not found.
    """
    country = None
    if parent_id == 0:
        country = to_country(jurisdiction)
        return country.alpha_3 if country else None

    if not country:
        subdivision = to_country_subdivision(jurisdiction)
        return subdivision.code if subdivision else None

    return country.alpha_3


def convert_year_to_dmy(year: str) -> str:
    """Converts a year to a year-month-day format (YYYYMMDD) string.
    :param int year: The year to convert.
    :return str: The converted year in year-month-day format.
    """
    year_int = int(year)

    dt = datetime(year_int, 1, 1)

    return dt.strftime("%Y%m%d")
