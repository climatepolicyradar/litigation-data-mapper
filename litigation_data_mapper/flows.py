import json
import logging
import os

import boto3
import requests
from prefect import flow
from pydantic import SecretStr

from litigation_data_mapper.cli import wrangle_data

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())

PARAMETER_BACKEND_APP_DOMAIN_NAME = "/Backend/API/App-Domain"
PARAMETER_BACKEND_SUPERUSER_EMAIL_NAME = "/Backend/API/SuperUser/Email"
PARAMETER_BACKEND_SUPERUSER_PASSWORD_NAME = "/Backend/API/SuperUser/Password"


@flow(log_prints=True)
def automatic_updates(debug=True):
    logger.info("🚀 Starting automatic litigation update flow.")

    try:
        output_file = os.path.join(os.getcwd(), "output.json")
        get_modified_data = True

        logger.info("📂 Using cached litigation data")
        cache_path = os.path.join(os.getcwd(), "litigation_raw_data_output.json")
        with open(cache_path, "r", encoding="utf-8") as f:
            litigation_data = json.load(f)

        # logger.info("🔍 Fetching litigation data")
        # litigation_data = fetch_litigation_data()

        mapped_data = wrangle_data(litigation_data, debug, get_modified_data)
        logger.info("✅ Finished mapping litigation data.")
        logger.info("🚀 Dumping litigation data to output file")

        logger.info(f"📝 Output file {output_file}")

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

        logger.info("✅ Finished dumping mapped litigation data.")

        logger.info("🚀 Triggering import into RDS")

        config = get_auth_config()
        auth_token = get_token(config)

        response = requests.get(
            f"https://{config['app_domain']}/api/v1/bulk-import/template/Litigation",
            headers={"Authorization": f"Bearer {auth_token}"},
            timeout=10,
        )

        logger.error(response.status_code)
        response.raise_for_status()

        received_data = response.json()

        file_path = "litigation_template.json"
        with open(file_path, "w") as f:
            json.dump(received_data, f, indent=4)
            logger.info("✅  Template successfully saved")

    except Exception as e:
        logger.exception(f"❌ Failed to run automatic updates. Error: {e}")
        raise


def get_token(config: dict[str, str]) -> str:
    """Get authentication token"""

    url = f"http://{config['app_domain']}/api/tokens"
    logger.info(f"🔒 Getting auth token for url: {url}")

    response = requests.post(
        url,
        timeout=10,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "username": config["superuser_email"].get_secret_value(),
            # "username": config["superuser_email"],
            "password": config["superuser_password"].get_secret_value(),
            # "password": config["superuser_password"],
        },
    )
    response.raise_for_status()

    logger.info("🔒 Got token")
    token = response.json()["access_token"]

    return token


def get_auth_config():
    logger.info("🔒 Fetching credentials from AWS...")
    return {
        "app_domain": get_ssm_parameter(PARAMETER_BACKEND_APP_DOMAIN_NAME),
        "superuser_email": SecretStr(
            get_ssm_parameter(PARAMETER_BACKEND_SUPERUSER_EMAIL_NAME)
        ),
        "superuser_password": SecretStr(
            get_ssm_parameter(PARAMETER_BACKEND_SUPERUSER_PASSWORD_NAME)
        ),
    }
    # return {
    #     "app_domain": "localhost:8888",
    #     "superuser_email": "user@navigator.com",
    #     "superuser_password": "password"
    # }


def get_ssm_parameter(param_name: str) -> str:
    """Get a parameter value from AWS SSM Parameter Store"""
    ssm = boto3.client("ssm", region_name="eu-west-1")
    response = ssm.get_parameter(Name=param_name, WithDecryption=True)
    return response["Parameter"]["Value"]


if __name__ == "__main__":
    automatic_updates()
