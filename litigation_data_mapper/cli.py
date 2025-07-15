import json
import os
import sys
from datetime import datetime, timedelta
from typing import Any

import click
import vcr

from litigation_data_mapper.datatypes import LitigationContext
from litigation_data_mapper.fetch_litigation_data import (
    LitigationType,
    fetch_litigation_data,
)
from litigation_data_mapper.parsers.collection import map_collections
from litigation_data_mapper.parsers.document import map_documents
from litigation_data_mapper.parsers.event import map_events
from litigation_data_mapper.parsers.family import map_families


@click.command()
@click.option(
    "--output_file",
    default=os.path.join(os.getcwd(), "output.json"),
    type=click.Path(exists=False),
)
@click.option("--debug/--no-debug", default=True)
@click.option(
    "--get-modified-data",
    default=False,
    help="Whether to map only recently modified litigation data",
)
@click.version_option("0.1.0", "--version", "-v", help="Show the version and exit.")
def entrypoint(
    output_file: str,
    debug: bool,
    get_modified_data: bool,
):
    """Simple program that wrangles litigation data into bulk import format.

    :param str output_file: The output filename.
    :param bool debug: Whether debug mode is on.
    :param bool get_modified_data: Whether to map only recently modified litigation data.
    """
    click.echo("🚀 Starting the litigation data mapping process.")

    try:
        click.echo("🚀 Mapping litigation data")
        click.echo("🔍 Fetching fresh litigation data")
        litigation_data: LitigationType = fetch_litigation_data()
        mapped_data = wrangle_data(litigation_data, debug, get_modified_data)
    except Exception as e:
        click.echo(f"❌ Failed to map litigation data to expected JSON. Error: {e}.")
        sys.exit(1)

    click.echo("✅ Finished mapping litigation data.")
    click.echo("🚀 Dumping litigation data to output file")
    dump_output(mapped_data, output_file, debug)
    click.echo("✅ Finished dumping mapped litigation data.")
    click.echo("📝 Mapped:")
    click.echo(f"   {len(mapped_data['collections'])} collections")
    click.echo(f"   {len(mapped_data['families'])} families")
    click.echo(f"   {len(mapped_data['documents'])} documents")
    click.echo(f"   {len(mapped_data['events'])} events")


@vcr.use_cassette(".cache/vcr_cassettes/entrypoint_with_vcr.yaml")  # type: ignore
def entrypoint_with_vcr():
    entrypoint()


def wrangle_data(
    data: LitigationType,
    debug: bool,
    get_modified_data: bool,
) -> dict[str, list[dict[str, Any]]]:
    """Put the mapped Litigation data into a dictionary ready for dumping.

    The output of this function will get dumped as JSON to the output
    file.

    :param dict[str, list[dict]] data: The litigation data.
    :param bool debug: Whether debug mode is on.
    :param bool get_modified_data: Whether to map all available litigation data.
    :return dict[str, list[Optional[dict[str, Any]]]]: The Litigation data
        mapped to the Document-Family-Collection-Event entity it
        corresponds to.
    """
    context = LitigationContext(
        failures=[],
        debug=debug,
        get_modified_data=get_modified_data,
        last_import_date=datetime.now() - timedelta(hours=48),
        case_bundles={},
        skipped_families=[],
        skipped_documents=[],
    )

    return {
        "collections": map_collections(data["collections"], context),
        "families": map_families(
            families_data=data["families"],
            concepts=data["concepts"],
            collections=data["collections"],
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
    entrypoint()
