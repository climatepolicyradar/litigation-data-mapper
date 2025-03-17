import json
import os
import sys
from typing import Any

import click

from litigation_data_mapper.fetch_litigation_data import (
    LitigationType,
    fetch_litigation_data,
)
from litigation_data_mapper.parsers.collection import map_collections
from litigation_data_mapper.parsers.document import map_documents
from litigation_data_mapper.parsers.family import map_families


@click.command()
@click.option(
    "--output_file",
    default=os.path.join(os.getcwd(), "output.json"),
    type=click.Path(exists=False),
)
@click.option("--debug/--no-debug", default=True)
@click.version_option("0.1.0", "--version", "-v", help="Show the version and exit.")
def entrypoint(output_file, debug: bool):
    """Simple program that wrangles litigation data into bulk import format.

    :param str output_file: The output filename.
    :param bool debug: Whether debug mode is on.
    """
    click.echo("🚀 Starting the litigation data mapping process.")

    try:
        click.echo("🚀 Mapping litigation data")
        litigation_data: LitigationType = fetch_litigation_data()
        mapped_data = wrangle_data(litigation_data)
    except Exception as e:
        click.echo(f"❌ Failed to map litigation data to expected JSON. Error: {e}.")
        sys.exit(1)

    click.echo("✅ Finished mapping litigation data.")
    click.echo("🚀 Dumping litigation data to output file")
    dump_output(mapped_data, output_file, debug)
    click.echo("✅ Finished dumping mapped litigation data.")


def wrangle_data(
    data: LitigationType,
    debug: bool = False,
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
    context = {}
    context["debug"] = debug
    return {
        "collections": map_collections(data["collections"], context),
        "families": map_families(data["families"], context),
        "documents": map_documents(
            {"documents": data["documents"], "families": data["families"]}, context
        ),
        "events": [],
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
