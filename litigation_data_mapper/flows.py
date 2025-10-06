import json
import logging
import os
from datetime import datetime, timezone

import boto3
import requests
from mypy_boto3_s3.client import S3Client
from prefect import flow, task
from pydantic import SecretStr

from litigation_data_mapper.cli import wrangle_data
from litigation_data_mapper.datatypes import Config, Credentials
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


@flow(log_prints=True, on_failure=[SlackNotify.message])
def sync_wordpress_to_s3_flow():
    sync_wordpress_s3_task_future = sync_wordpress_to_s3_task.submit()
    sync_wordpress_s3_task_future.result()
    logger.info("✅ sync_wordpress_s3_task_future successful.")

    get_deletions_task_future = get_deletions_task.submit()
    get_deletions_task_future.result()
    logger.info("✅ get_deletions_task_future successful.")


@task
def sync_wordpress_to_s3_task():
    sync_wordpress_to_s3()


def sync_wordpress_to_s3():
    client = boto3.client("s3", region_name="eu-west-1")
    now = datetime.now(tz=timezone.utc).isoformat()

    for endpoint in endpoints:
        data = fetch_word_press_data(
            f"https://admin.climatecasechart.com/wp-json/wp/v2/{endpoint}"
        )

        client.put_object(
            Bucket="cpr-cache",
            Key=f"litigation/wordpress/{endpoint}.json",
            Body=json.dumps(data),
        )
        client.put_object(
            Bucket="cpr-cache",
            Key=f"litigation/wordpress/{now}/{endpoint}.json",
            Body=json.dumps(data),
        )


def load_s3_object(client: S3Client, taxonomy: str):
    s3_object = client.get_object(
        Bucket="cpr-cache", Key=f"litigation/wordpress/{taxonomy}.json"
    )
    data = s3_object["Body"].read().decode("utf-8")
    return json.loads(data)


@task
def get_deletions_task():
    get_deletions()


def get_deletions():
    now = datetime.now(tz=timezone.utc).isoformat()

    client = boto3.client("s3", region_name="eu-west-1")

    non_us_case_list = load_s3_object(client, "non_us_case")
    case_list = load_s3_object(client, "case")

    case_ids = [case["id"] for case in non_us_case_list + case_list]
    family_ids = [f"Sabin.family.{case_id}.0" for case_id in case_ids]

    # Paginate through CPR Families API until empty page returned
    family_ids = []
    page = 1
    while True:
        resp = requests.get(
            "https://api.climatepolicyradar.org/families/",
            params={
                "corpus.import_id": "Academic.corpus.Litigation.n0000",
                "page": page,
            },
            timeout=10,
        )
        resp.raise_for_status()
        families_data = resp.json().get("data", [])
        family_id_data = [family["import_id"] for family in families_data]
        family_ids.extend(family_id_data)
        if not families_data:
            break

        page += 1

    client.put_object(
        Bucket="cpr-cache",
        Key="litigation/state/deletions.json",
        Body=json.dumps(family_ids),
    )
    client.put_object(
        Bucket="cpr-cache",
        Key=f"litigation/state/{now}/deletions.json",
        Body=json.dumps(family_ids),
    )

    return family_ids


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

    # Get the results of the paralleltasks
    bulk_input_response = bulk_input_response_future.result()
    logger.info(
        f"✅ bulk_input_response completed successfully with response: {bulk_input_response.status_code}."
    )

    logger.info(f"✅ {bulk_input_response.status_code} from trigger_bulk_import.")


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
