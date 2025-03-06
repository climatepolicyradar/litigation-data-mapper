from typing import Any, Dict


def _get_nested_keys(d: Dict[str, Any], parent_key: str = "") -> set:
    """
    Retrieve all keys from a dictionary, including nested keys, as dot-separated paths,
    while excluding specific fields.

    This function recursively traverses through the dictionary, including nested dictionaries,
    to generate a set of keys represented as dot-separated paths (e.g., 'parent.child').
    Additionally, it allows certain fields to be excluded from the key set.

    :param Dict[str, Any] d: The dictionary from which to extract keys.
    :param str parent_key: A string used to accumulate the key path during recursion.
                        It should be empty for the initial call.
    :return set : A set of strings representing all keys (including nested keys)
             as dot-separated paths, excluding the specified `excluded_fields`.
    """

    # Exclude word press related keys
    excluded_keys = ["yoast_head_json", "_links", "yoast_head"]

    keys = set()
    for key, value in d.items():
        if key in excluded_keys:
            continue

        keys.add(key)
        if isinstance(value, dict):
            keys.update(_get_nested_keys(value))
    return keys


def verify_required_fields_present(
    data: dict[str, Any], required_fields: set[str]
) -> bool:
    """Verify that the required fields are present in the data.

    :param dict[str, Any] data: The data to check.
    :param set[str] required_fields: The required data fields.
    :raise AttributeError if any of the required fields are missing.
    :return bool: True if the data contains the required fields.
    """
    data_keys = _get_nested_keys(data)
    diff = set(required_fields).difference(data_keys)
    if diff == set():
        return True

    # sets are naturally un-ordered,
    # sorting them means we can test the error message reliably
    sorted_diff = sorted(diff)
    sorted_cols = sorted(data_keys)

    raise AttributeError(
        f"Required fields {sorted_diff} not present in data: {sorted_cols}"
    )
