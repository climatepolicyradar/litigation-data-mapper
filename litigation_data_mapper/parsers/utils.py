from typing import Optional

import pycountry
from pycountry.db import Country


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


def to_iso(country: Country) -> str:
    """
    Convert a pycountry country object to its ISO alpha-3 code.

    :param country: A pycountry country object.
    :return str: The ISO alpha-3 code of the country, or an empty string if the country is None.
    """
    return country.alpha_3
