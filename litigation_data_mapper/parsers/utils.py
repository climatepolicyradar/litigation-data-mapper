from typing import Optional

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

    country_obj = pycountry.countries.get(name=country)

    return country_obj


def to_country_subdivision(subdivision: str) -> Optional[Subdivision]:
    """
    Convert a country subdivision name to a pycountry subdivision object.

    :param str subdivision: The name of the country subdivision.
    :return: A pycountry subdivision object or None if not found.
    """

    related_territories = pycountry.countries.search_fuzzy(subdivision)
    parent_territory = (
        related_territories[0].data_class if related_territories else None
    )
    # On the Existing Countries class, which is the result of the search_fuzzy method,
    # we can access the data_class attribute to get the actual Country object.

    if not parent_territory:
        return None

    country = to_country(str(parent_territory))

    if not country:
        return None

    subdivision_hierarchies = pycountry.subdivisions.get(country_code=country.alpha_2)

    if not subdivision_hierarchies:
        return None

    subdivision_hierarchy = next(
        (
            subdivision
            for subdivision in subdivision_hierarchies
            if subdivision.name == subdivision
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
        return subdivision.alpha_2 if subdivision else None

    return country.alpha_3
