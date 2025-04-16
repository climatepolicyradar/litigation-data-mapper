import json
import os
import sys
from typing import Any

import click
from prefect import flow

from litigation_data_mapper.datatypes import LitigationContext
from litigation_data_mapper.fetch_litigation_data import (
    LitigationType,
    fetch_litigation_data,
)
from litigation_data_mapper.parsers.collection import map_collections
from litigation_data_mapper.parsers.document import map_documents
from litigation_data_mapper.parsers.event import map_events
from litigation_data_mapper.parsers.family import map_families


@flow(log_prints=True)
def trigger_pipeline_automatic_updates(use_cache=True, debug=True):
    click.echo("🚀 Starting automatic litigation update flow.")

    try:
        cache_file = "litigation_raw_data_output.json"
        output_file = os.path.join(os.getcwd(), "output.json")
        cache_path = os.path.join(os.getcwd(), cache_file)

        if use_cache and os.path.exists(cache_path):
            click.echo(f"📂 Using cached litigation data from {cache_file}")
            with open(cache_path, "r", encoding="utf-8") as f:
                litigation_data = json.load(f)
        else:
            click.echo("🔍 Fetching fresh litigation data")
            litigation_data = fetch_litigation_data()
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(litigation_data, f, ensure_ascii=False, indent=2)
            click.echo(f"💾 Cached raw litigation data to {cache_file}")

        mapped_data = wrangle_data(litigation_data, debug)
        click.echo("✅ Finished mapping litigation data.")
        click.echo("🚀 Dumping litigation data to output file")
        dump_output(mapped_data, output_file, debug)

        if os.path.exists(output_file):
            click.echo(f"✅ Output file successfully created at: {output_file}.")
        else:
            click.echo("❌ Output file was not found after writing.")
            raise FileNotFoundError(f"{output_file} does not exist after dump_output.")

        click.echo("✅ Finished dumping mapped litigation data.")

        click.echo("✅ Finished dumping mapped litigation data.")
    except Exception as e:
        click.echo(f"❌ Failed to run automatic updates. Error: {e}")
        raise


@click.command()
@click.option(
    "--output_file",
    default=os.path.join(os.getcwd(), "output.json"),
    type=click.Path(exists=False),
)
@click.option("--debug/--no-debug", default=True)
@click.option(
    "--cache-file",
    default="litigation_raw_data_output.json",
    help="File to cache raw litigation data",
)
@click.option(
    "--use-cache/--no-use-cache",
    default=False,
    help="Whether to use cached data if available",
)
@click.version_option("0.1.0", "--version", "-v", help="Show the version and exit.")
def entrypoint(output_file: str, debug: bool, cache_file: str, use_cache: bool):
    """Simple program that wrangles litigation data into bulk import format.

    :param str output_file: The output filename.
    :param bool debug: Whether debug mode is on.
    """
    click.echo("🚀 Starting the litigation data mapping process.")

    try:
        click.echo("🚀 Mapping litigation data")
        cache_path = os.path.join(os.getcwd(), cache_file)
        if use_cache and os.path.exists(cache_path):
            click.echo(f"📂 Using cached litigation data from {cache_file}")
            with open(cache_path, "r", encoding="utf-8") as f:
                litigation_data = json.load(f)
        else:
            click.echo("🔍 Fetching fresh litigation data")
            litigation_data: LitigationType = fetch_litigation_data()
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(litigation_data, f, ensure_ascii=False, indent=2)
            click.echo(f"💾 Cached raw litigation data to {cache_file}")
        mapped_data = wrangle_data(litigation_data, debug)
    except Exception as e:
        click.echo(f"❌ Failed to map litigation data to expected JSON. Error: {e}.")
        sys.exit(1)

    click.echo("✅ Finished mapping litigation data.")
    click.echo("🚀 Dumping litigation data to output file")
    dump_output(mapped_data, output_file, debug)
    click.echo("✅ Finished dumping mapped litigation data.")


def wrangle_data(
    data: LitigationType,
    debug: bool,
) -> dict[str, list[dict[str, Any]]]:
    """Put the mapped Litigation data into a dictionary ready for dumping.

    The output of this function will get dumped as JSON to the output
    file.

    :param dict[str, list[dict]] data: The litigation data.
    :param bool debug: Whether debug mode is on.
    :return dict[str, list[Optional[dict[str, Any]]]]: The Litigation data
        mapped to the Document-Family-Collection-Event entity it
        corresponds to.
    """
    context = LitigationContext(
        failures=[],
        debug=debug,
        case_bundles={},
        skipped_families=[],
        skipped_documents=[],
    )

    return {
        "collections": map_collections(data["collections"], context),
        "families": map_families(
            families_data=data["families"],
            concepts=data["concepts"],
            context=context,
        ),
        "documents": map_documents(
            {"documents": data["documents"], "families": data["families"]}, context
        ),
        "events": map_events(data["families"], context),
    }


def dump_output(
    mapped_data: dict[str, list[dict[str, Any]]],
    output_file: str,
    debug: bool = False,
):
    """Dump the wrangled JSON to the output file.

    :param dict[str, list[Optional[dict[str, Any]]]] mapped_data: The
        mapped Litigation data.
    :param str output_file: The output filename.
    :param bool debug: Whether debug mode is on.
    """
    if debug:
        click.echo(f"📝 Output file {click.format_filename(output_file)}")

    try:
        with open(output_file, "w+", encoding="utf-8") as f:
            json.dump(mapped_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        click.echo(f"❌ Failed to dump JSON to file. Error: {e}.")
        sys.exit(1)


if __name__ == "__main__":
    # entrypoint()
    trigger_pipeline_automatic_updates()
