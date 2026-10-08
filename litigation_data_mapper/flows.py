import json
import logging
import os
import time
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Literal, Optional

import boto3
import requests
from botocore.exceptions import BotoCoreError, ClientError
from mypy_boto3_s3.client import S3Client
from prefect import flow, task
from prefect.artifacts import create_table_artifact
from pydantic import SecretStr

from litigation_data_mapper.cli import wrangle_data
from litigation_data_mapper.datatypes import Config, Credentials
from litigation_data_mapper.fetch_litigation_data import (
    LitigationType,
    fetch_litigation_data,
)
from litigation_data_mapper.utils import SlackNotify, get_ssm_parameter
from litigation_data_mapper.wordpress import fetch_word_press_data
from litigation_data_mapper.wordpress_data import endpoints

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())

PARAMETER_ADMIN_BACKEND_APP_DOMAIN_NAME = "/Admin-Backend/API/App-Domain"
PARAMETER_BACKEND_SUPERUSER_EMAIL_NAME = "/Backend/API/SuperUser/Email"
PARAMETER_BACKEND_SUPERUSER_PASSWORD_NAME = "/Backend/API/SuperUser/Password"  # nosec
# TODO: placeholder - confirm this parameter exists in each environment, or create it.
PARAMETER_ADMIN_BACKEND_BULK_IMPORT_BUCKET_NAME = (
    "/Admin-Backend/Bulk-Import/Bucket-Name"
)

BULK_IMPORT_POLL_INTERVAL_SECONDS = 30
# Imports typically take around 5 minutes but have a long tail, so this is a ceiling
# that lets a slow import finish rather than an estimate of how long one takes.
BULK_IMPORT_TIMEOUT_SECONDS = 2 * 60 * 60


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
def trigger_bulk_import(litigation_data: LitigationType) -> str:
    [mapped_data, failures] = wrangle_data(
        litigation_data, debug=True, get_modified_data=False
    )
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

    logger.info("📝 Dumping skipped data to error log")
    error_log = os.path.join(os.getcwd(), "error_log.txt")
    try:
        create_table_artifact(
            key="error-log",
            table=[asdict(failure) for failure in failures],
            description="List of Sabin ids of data that could not be mapped with reasons",
        )

    except Exception as e:
        logger.error(f"❌ Failed to write error log to file. Error: {e}.")

    if os.path.exists(error_log):
        logger.info(f"✅ Error log successfully created at: {error_log}.")
    else:
        logger.error("❌ Error log was not found after writing.")
        raise FileNotFoundError(f"{error_log} does not exist after dump_output.")

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

    import_id = response.json()["import_id"]
    logger.info(f"✅ Bulk import {import_id} accepted by the admin service.")

    return import_id


def get_bulk_import_outcome(
    client: S3Client, bucket: str, import_id: str
) -> Optional[tuple[Literal["result", "failure"], dict[str, Any]]]:
    """
    Get the outcome of a bulk import from the files the admin service writes to S3.

    The admin service names them `{import_id}-result-...` or `{import_id}-failure-...`,
    and only writes them once the import, and the database dump after it, has finished.

    :param S3Client client: The S3 client to read the bucket with.
    :param str bucket: The admin service's bulk import bucket.
    :param str import_id: The id of the bulk import, as returned when it was triggered.
    :return: The kind of outcome and the file's contents, or None if still running.
    """
    for outcome in ("result", "failure"):
        response = client.list_objects_v2(
            Bucket=bucket, Prefix=f"{import_id}-{outcome}-", MaxKeys=1
        )
        keys = [obj["Key"] for obj in response.get("Contents", []) if "Key" in obj]
        if keys:
            obj = client.get_object(Bucket=bucket, Key=keys[0])
            return outcome, json.loads(obj["Body"].read())
    return None


def await_bulk_import(import_id: str) -> None:
    """
    Wait for a bulk import to finish, by polling S3 for the outcome the admin service writes.

    The bulk import endpoint returns as soon as the data it was given is validated and
    runs the import itself in the background, so a 202 from it only means the data was
    accepted. Flows downstream of this one read the data the import writes, so we wait
    for the import to actually finish rather than assuming it has.

    :param str import_id: The id of the bulk import, as returned when it was triggered.
    :raises RuntimeError: raised if the bulk import failed.
    :raises TimeoutError: raised if the bulk import did not finish in time.
    """
    bucket = get_ssm_parameter(PARAMETER_ADMIN_BACKEND_BULK_IMPORT_BUCKET_NAME)
    client: S3Client = boto3.client("s3", region_name="eu-west-1")
    deadline = time.monotonic() + BULK_IMPORT_TIMEOUT_SECONDS

    logger.info(f"⏳ Waiting for bulk import {import_id} to complete.")

    while True:
        try:
            outcome = get_bulk_import_outcome(client, bucket, import_id)
        except (BotoCoreError, ClientError) as e:
            # A transient S3 error tells us nothing about the import itself, so keep
            # polling until the deadline.
            logger.warning(f"⚠️ Could not read bulk import outcome. Error: {e}.")
        else:
            if outcome is not None:
                kind, contents = outcome
                if kind == "failure":
                    raise RuntimeError(
                        f"❌ Bulk import {import_id} failed. "
                        f"Error: {contents.get('error')}."
                    )

                counts = {entity: len(ids) for entity, ids in contents.items()}
                logger.info(f"✅ Bulk import {import_id} completed. Saved: {counts}.")
                return

            logger.info(f"⏳ Bulk import {import_id} is still running.")

        if time.monotonic() >= deadline:
            raise TimeoutError(
                f"❌ Bulk import {import_id} did not complete within "
                f"{BULK_IMPORT_TIMEOUT_SECONDS} seconds."
            )

        time.sleep(BULK_IMPORT_POLL_INTERVAL_SECONDS)


@task
def await_bulk_import_task(import_id: str) -> None:
    await_bulk_import(import_id)


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
    family_ids_from_wordpress = [f"Sabin.family.{case_id}.0" for case_id in case_ids]

    # Paginate through CPR Families API until empty page returned
    missing_family_ids = []
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
        families_data_from_api = resp.json().get("data", [])
        if not families_data_from_api:
            break

        missing_family_id_data = [
            family["import_id"]
            for family in families_data_from_api
            if family["import_id"] not in family_ids_from_wordpress
        ]
        missing_family_ids.extend(missing_family_id_data)

        page += 1

    client.put_object(
        Bucket="cpr-cache",
        Key="litigation/state/deletions.json",
        Body=json.dumps(missing_family_ids),
    )
    client.put_object(
        Bucket="cpr-cache",
        Key=f"litigation/state/{now}/deletions.json",
        Body=json.dumps(missing_family_ids),
    )

    return missing_family_ids


@flow(log_prints=True, on_failure=[SlackNotify.message])
def automatic_updates(debug=True):
    """
    Prefect flow which pulls down all data from the Sabin API, filters it to only contain data created or updated in the last 24 hrs,
    maps it to a json file and sends that file to the admin service API to trigger a bulk import/update.
    """
    logger.info("🚀 Starting automatic litigation update flow.")

    litigation_data = fetch_litigation_data_task.submit().result()
    import_id = trigger_bulk_import.submit(litigation_data).result()

    # The import runs in the background in the admin service, so this flow is only
    # done once that import is, otherwise flows downstream of it read partial data.
    await_bulk_import_task.submit(import_id).result()

    logger.info(f"✅ Automatic litigation update flow completed. Import: {import_id}.")


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
