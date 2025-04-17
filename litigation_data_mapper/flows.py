import logging
import os

from prefect import flow

from litigation_data_mapper.cli import dump_output, fetch_litigation_data, wrangle_data

logger = logging.getLogger(__name__)


@flow(log_prints=True)
def automatic_updates(debug=True):
    logger.info("🚀 Starting automatic litigation update flow.")

    try:
        output_file = os.path.join(os.getcwd(), "output.json")

        logger.info("🔍 Fetching litigation data")
        litigation_data = fetch_litigation_data()

        mapped_data = wrangle_data(litigation_data, debug)
        logger.info("✅ Finished mapping litigation data.")
        logger.info("🚀 Dumping litigation data to output file")
        dump_output(mapped_data, output_file, debug)

        if os.path.exists(output_file):
            logger.info(f"✅ Output file successfully created at: {output_file}.")
        else:
            logger.error("❌ Output file was not found after writing.")
            raise FileNotFoundError(f"{output_file} does not exist after dump_output.")

        logger.info("✅ Finished dumping mapped litigation data.")
    except Exception as e:
        logger.exception(f"❌ Failed to run automatic updates. Error: {e}")
        raise
