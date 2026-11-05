import json
import logging
import os
import time
from dataclasses import asdict

import boto3
import requests
from botocore.exceptions import BotoCoreError, ClientError
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

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())

PARAMETER_ADMIN_BACKEND_APP_DOMAIN_NAME = "/Admin-Backend/API/App-Domain"
PARAMETER_BACKEND_SUPERUSER_EMAIL_NAME = "/Backend/API/SuperUser/Email"
PARAMETER_BACKEND_SUPERUSER_PASSWORD_NAME = "/Backend/API/SuperUser/Password"  # nosec
PARAMETER_ADMIN_BACKEND_BULK_IMPORT_BUCKET_NAME = (
    "/Admin-Backend/Bulk-Import/Bucket-Name"
)


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
    return response


def is_aws_error(task, task_run, state) -> bool:
    return isinstance(
        state.result(raise_on_failure=False), (BotoCoreError, ClientError)
    )


@task(retries=3, retry_delay_seconds=60, retry_condition_fn=is_aws_error)
def await_bulk_import(import_uuid: str, timeout_seconds: int = 2 * 60 * 60) -> None:
    """Wait for the admin service to write the bulk import's result or failure file to S3."""
    client = boto3.client("s3", region_name="eu-west-1")
    bucket = get_ssm_parameter(PARAMETER_ADMIN_BACKEND_BULK_IMPORT_BUCKET_NAME)
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        response = client.list_objects_v2(Bucket=bucket, Prefix=f"{import_uuid}-")
        keys = [obj.get("Key", "") for obj in response.get("Contents", [])]
        if any(key.startswith(f"{import_uuid}-failure-") for key in keys):
            raise RuntimeError(f"❌ Bulk import {import_uuid} failed.")
        if any(key.startswith(f"{import_uuid}-result-") for key in keys):
            return
        time.sleep(30)

    raise TimeoutError(
        f"❌ Bulk import {import_uuid} did not finish within {timeout_seconds} seconds."
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

    # Get the results of the paralleltasks
    bulk_input_response = bulk_input_response_future.result()
    logger.info(
        f"✅ bulk_input_response completed successfully with response: {bulk_input_response.status_code}."
    )

    import_uuid = bulk_input_response.json()["import_uuid"]
    logger.info(
        f"✅ {bulk_input_response.status_code} from trigger_bulk_import, import_uuid: {import_uuid}."
    )

    await_bulk_import(import_uuid)


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
