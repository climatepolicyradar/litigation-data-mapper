import json
import os
import sys
from datetime import datetime, timedelta
from typing import Any

import click
import vcr

from litigation_data_mapper.datatypes import LitigationContext
from litigation_data_mapper.extract_concepts import (
    Concept,
)
from litigation_data_mapper.extract_concepts import taxonomies as concept_taxonomies
from litigation_data_mapper.extract_concepts import (
    transform_wordpress_concepts_data,
)
from litigation_data_mapper.fetch_litigation_data import (
    LitigationType,
    fetch_litigation_data,
)
from litigation_data_mapper.parsers.collection import map_collections
from litigation_data_mapper.parsers.document import map_documents
from litigation_data_mapper.parsers.event import map_events
from litigation_data_mapper.parsers.family import (
    get_jurisdiction_iso_codes,
    map_families,
    process_global_case_data,
    process_us_case_data,
)
from litigation_data_mapper.parsers.helpers import map_global_jurisdictions
from litigation_data_mapper.wordpress_data import fetch_and_write_all_wordpress_data


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


def load_json_data(taxonomy: str):
    with open(f"./build/wordpress/{taxonomy}.json", "r") as f:
        return json.load(f)


@click.command()
@vcr.use_cassette(".cache/vcr_cassettes/transform_single_case.yaml")  # type: ignore
@click.option(
    "--case_id",
    required=True,
)
def transform_single_case(case_id: str):
    [entrypoint, id] = case_id.split("/")
    print(f"Transforming single case with ID: {entrypoint, id}")

    fetch_and_write_all_wordpress_data()

    concepts: dict[int, Concept] = {}
    for concept_taxonomy in concept_taxonomies:
        concepts_data = load_json_data(concept_taxonomy)
        transformed_concepts_data = transform_wordpress_concepts_data(
            data=concepts_data, taxonomy=concept_taxonomy
        )
        concepts.update(transformed_concepts_data)

    if entrypoint == "non_us_case":
        entrypoint_json = load_json_data(entrypoint)

        mapped_jurisdictions = map_global_jurisdictions(load_json_data("jurisdiction"))

        case = next(case for case in entrypoint_json if case["id"] == int(id))
        processed_case = process_global_case_data(
            family_data=case,
            geographies=get_jurisdiction_iso_codes(
                family=case, mapped_jurisdictions=mapped_jurisdictions
            ),
            case_id=int(id),
            concepts=concepts,
        )

        print(json.dumps(processed_case, indent=2))

    if entrypoint == "case":
        entrypoint_json = load_json_data(entrypoint)

        case_bundles = load_json_data("case_bundle")

        case = next(case for case in entrypoint_json if case["id"] == int(id))
        processed_case = process_us_case_data(
            family_data=case,
            case_id=int(id),
            context=LitigationContext(
                failures=[],
                debug=True,
                get_modified_data=False,
                last_import_date=datetime.strptime(
                    "2020-01-01T12:00:00", "%Y-%m-%dT%H:%M:%S"
                ),
                case_bundles={
                    case_bundle["id"]: {
                        "description": case_bundle.get("acf", {}).get("ccl_core_object")
                    }
                    for case_bundle in case_bundles
                },
                skipped_families=[],
                skipped_documents=[],
            ),
            concepts=concepts,
            collections=case_bundles,
        )

        print(json.dumps(processed_case, indent=2))


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
