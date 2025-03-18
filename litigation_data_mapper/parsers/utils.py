from datetime import datetime
from typing import Optional

import click
import pycountry
from pycountry.db import Country, Subdivision


def to_country(country: str) -> Optional[Country]:
    """
    Convert a country name to a pycountry country object.

    :param str country: The name of the country.
    :return: A pycountry country object or None if not found.
    """

    if not country:
        return None

    try:
        country_obj = pycountry.countries.get(name=country)
        return country_obj
    except LookupError:
        return None


def to_country_subdivision(territory: str) -> Optional[Subdivision]:
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


def get_jurisdiction_iso(jurisdiction: str) -> Optional[str]:
    """
    This function takes a jurisdiction name and returns the corresponding ISO code.
    ISO 3166-2 for subdivisions
    ISO 3166-1 alpha-3 for countries

    :param str jurisdiction: The name of the jurisdiction.
    :return str: The ISO code of the jurisdiction, or None if the jurisdiction is not found.
    """
    country = to_country(jurisdiction)

    if not country:
        subdivision = to_country_subdivision(jurisdiction)
        return subdivision.code if subdivision else None

    return country.alpha_3


def convert_year_to_dmy(year: str) -> Optional[str]:
    """Converts a year to a day-month-year format string.

    :param int year: The year to convert.

    :return Optional[str]: The converted year in day-month-year format, or None if the year cannot be converted.
    """
    try:
        year_int = int(year)

        dt = datetime(year_int, 1, 1)

        return dt.strftime("%Y%m%d")
    except ValueError:
        click.echo(f"🔥 Could not convert year to integer: {year}")
        return None
