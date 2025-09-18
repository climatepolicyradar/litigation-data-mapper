import json

import boto3
import requests


def main():
    client = boto3.client("s3", region_name="eu-west-1")

    print("Fetching case_bundle.json from S3")
    case_bundle_s3_object = client.get_object(
        Bucket="cpr-cache", Key="litigation/wordpress/case_bundle.json"
    )
    case_bundle_list = json.loads(case_bundle_s3_object["Body"].read().decode("utf-8"))

    print("Fetching non_us_case.json from S3")
    non_us_case_s3_object = client.get_object(
        Bucket="cpr-cache", Key="litigation/wordpress/non_us_case.json"
    )
    non_us_case_list = json.loads(non_us_case_s3_object["Body"].read().decode("utf-8"))

    print("Generating redirects for cases")
    redirects = []
    for case in non_us_case_list:
        id = case["id"]
        slug = case["slug"]

        api_url = f"https://api.climatepolicyradar.org/families/Sabin.family.{id}.0"
        r = requests.get(api_url, timeout=10)
        api_json = r.json()

        if r.status_code != 200:
            print(r.status_code)
            print(id)
            print(slug)
        api_slug = api_json["data"]["slug"]
        redirect = {"Key": f"/non-us-case/{slug}", "Value": f"/document/{api_slug}"}
        redirects.append(redirect)

    print("Generating redirects for cases bundles")
    for case_bundle in case_bundle_list:
        id = case_bundle["id"]
        slug = case_bundle["slug"]

        api_url = f"https://api.climatepolicyradar.org/families/collections/Sabin.collection.{id}.0"
        r = requests.get(api_url, timeout=10)
        api_json = r.json()

        if r.status_code != 200:
            print(r.status_code)
            print(id)
            print(slug)

        api_slug = api_json["data"]["slug"]
        redirect = {"Key": f"/case/{slug}", "Value": f"/collections/{api_slug}"}
        redirects.append(redirect)

    print(f"Generated {len(redirects)} redirects, writing to redirects.json")
    with open("./build/redirects.json", "w+", encoding="utf-8") as f:
        json.dump(redirects, f, indent=2)
