import json
import logging
import os

import boto3
import requests
from prefect import flow, task
from pydantic import SecretStr

from litigation_data_mapper.cli import wrangle_data
from litigation_data_mapper.datatypes import Config, Credentials
from litigation_data_mapper.extract_concepts import Concept
from litigation_data_mapper.fetch_litigation_data import (
    LitigationType,
    fetch_litigation_data,
)
from litigation_data_mapper.utils import SlackNotify
from litigation_data_mapper.wordpress import fetch_word_press_data
from litigation_data_mapper.wordpress_data import endpoints

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())

PARAMETER_ADMIN_BACKEND_APP_DOMAIN_NAME = "/Admin-Backend/API/App-Domain"
PARAMETER_BACKEND_SUPERUSER_EMAIL_NAME = "/Backend/API/SuperUser/Email"
PARAMETER_BACKEND_SUPERUSER_PASSWORD_NAME = "/Backend/API/SuperUser/Password"  # nosec


@task
def fetch_litigation_data_task() -> LitigationType:
    try:
        logger.info("🔍 Fetching litigation data")
        litigation_data = fetch_litigation_data()
        return litigation_data

    except Exception as e:
        logger.exception(f"❌ Failed to run automatic updates. Error: {e}")
        raise


@task
def trigger_bulk_import(litigation_data: LitigationType) -> requests.models.Response:
    mapped_data = wrangle_data(litigation_data, debug=True, get_modified_data=True)
    logger.info("✅ Finished mapping litigation data.")
    logger.info("📝 Dumping litigation data to output file")
    output_file = os.path.join(os.getcwd(), "output.json")
    try:
        with open(output_file, "w+", encoding="utf-8") as f:
            json.dump(mapped_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"❌ Failed to dump JSON to file. Error: {e}.")

    if os.path.exists(output_file):
        logger.info(f"✅ Output file successfully created at: {output_file}.")
    else:
        logger.error("❌ Output file was not found after writing.")
        raise FileNotFoundError(f"{output_file} does not exist after dump_output.")

    logger.info("🚀 Triggering import into RDS")

    config = get_auth_config()
    auth_token = get_token(config)

    response = requests.post(
        f"https://{config.app_domain}/api/v1/bulk-import/{config.corpus_import_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        files={"data": open(output_file, "rb")},
        timeout=10,
    )

    response.raise_for_status()
    return response


@task
def sync_concepts_to_s3(concepts_dict: dict[int, Concept]) -> list[Concept]:
    concepts = list(concepts_dict.values())
    client = boto3.client("s3", region_name="eu-west-1")

    # empty the bucket
    s3 = boto3.resource("s3", region_name="eu-west-1")
    # the bucket name is hardcoded for now while we get this working
    bucket = s3.Bucket("cpr-cache")
    bucket.objects.all().delete()

    for concept in concepts:
        client.put_object(
            Bucket="cpr-cache",
            # we use the `__` as a namespace as
            # - / would put it in a different folder`
            # - _ is used in the concept.type
            # - . is used in the concept.id
            Key=f"litigation/concepts/{concept.type}__{concept.id}.json",
            Body=json.dumps(concept._asdict()),
        )
    return concepts


@task
def sync_wordpress_to_s3():
    client = boto3.client("s3", region_name="eu-west-1")

    for endpoint in endpoints:
        data = fetch_word_press_data(
            f"https://admin.climatecasechart.com/wp-json/wp/v2/{endpoint}"
        )

        client.put_object(
            Bucket="cpr-cache",
            Key=f"litigation/wordpress/{endpoint}.json",
            Body=json.dumps(data),
        )


@flow(log_prints=True, on_failure=[SlackNotify.message])
def automatic_updates(debug=True):
    """
    Prefect flow which pulls down all data from the Sabin API, filters it to only contain data created or updated in the last 24 hrs,
    maps it to a json file and sends that file to the admin service API to trigger a bulk import/update.
    """
    logger.info("🚀 Starting automatic litigation update flow.")

    # Fan-out and start parallel tasks
    litigation_data = fetch_litigation_data_task.submit().result()
    bulk_input_response_future = trigger_bulk_import.submit(litigation_data)
    sync_concepts_to_s3_future = sync_concepts_to_s3.submit(litigation_data["concepts"])
    sync_wordpress_s3_future = sync_wordpress_to_s3.submit()

    # Get the results of the paralleltasks
    bulk_input_response = bulk_input_response_future.result()
    logger.info(
        f"✅ bulk_input_response completed successfully with response: {bulk_input_response.status_code}."
    )

    sync_wordpress_s3_future.result()
    logger.info("✅ WordPress data synced to S3 successfully.")

    concepts_dict = sync_concepts_to_s3_future.result()
    logger.info(f"✅ {len(concepts_dict)} Concepts synced to S3 successfully.")


def get_token(config: Config) -> str:
    """
    Get authentication token

    :param Config: Object containing user credentials needed to obtain an auth token.
    :return str: An auth token.
    """

    url = f"https://{config.app_domain}/api/tokens"
    logger.info(f"🔒 Getting auth token for url: {url}")

    response = requests.post(
        url,
        timeout=10,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "username": config.user_credentials.superuser_email.get_secret_value(),
            "password": config.user_credentials.superuser_password.get_secret_value(),
        },
    )
    response.raise_for_status()

    logger.info("🔒 Got token")

    return response.json()["access_token"]


def get_auth_config() -> Config:
    """
    Get config needed to trigger bulk import.

    :return Config: An object containing config needed for bulk import.
    """

    logger.info("🔒 Fetching credentials from AWS...")
    credentials = Credentials(
        superuser_email=SecretStr(
            get_ssm_parameter(PARAMETER_BACKEND_SUPERUSER_EMAIL_NAME)
        ),
        superuser_password=SecretStr(
            get_ssm_parameter(PARAMETER_BACKEND_SUPERUSER_PASSWORD_NAME)
        ),
    )

    return Config(
        corpus_import_id="Academic.corpus.Litigation.n0000",
        app_domain=get_ssm_parameter(PARAMETER_ADMIN_BACKEND_APP_DOMAIN_NAME),
        user_credentials=credentials,
    )


def get_ssm_parameter(param_name: str) -> str:
    """
    Get a parameter value from AWS SSM Parameter Store

    :param str param_name: Name of the parameter to be fetched.
    :return str: The value of the parameter as set in AWS.
    """
    ssm = boto3.client("ssm", region_name="eu-west-1")
    response = ssm.get_parameter(Name=param_name, WithDecryption=True)
    return response["Parameter"]["Value"]
