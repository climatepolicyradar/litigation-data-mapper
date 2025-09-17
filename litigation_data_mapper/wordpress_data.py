import json
import os

from litigation_data_mapper.wordpress import fetch_word_press_data

endpoints = [
    "case_bundle",
    "case",
    "non_us_case",
    "media",
    # USA
    "case_category",
    "entity",  # This is like a jurisdiction but for USA
    "principal_law",
    # Non-USA
    "jurisdiction",
    "non_us_principal_law",
    "non_us_case_category",
]


def fetch_and_write_all_wordpress_data():
    all_data = {}
    os.makedirs("./build/wordpress", exist_ok=True)

    for endpoint in endpoints:
        data = fetch_word_press_data(
            f"https://climatecasechart.com/wp-json/wp/v2/{endpoint}"
        )

        with open(f"./build/wordpress/{endpoint}.json", "w") as f:
            json.dump(data, f)

        all_data[endpoint] = data

    return all_data
