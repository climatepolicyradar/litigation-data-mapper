import importlib.metadata
import os
import sys

import click

PACKAGE_NAME = "{{cookiecutter.package_name}}"


@click.command()
@click.option(
    "--output_file",
    default=os.path.join(os.getcwd(), "output.json"),
    type=click.Path(exists=False),
)
@click.option("--debug/--no-debug", default=True)
@click.version_option(
    importlib.metadata.version(PACKAGE_NAME),
    "--version",
    "-v",
    help="Show the version and exit.",
)
def entrypoint(output_file, debug: bool):
    """Simple program that wrangles {{cookiecutter.corpus_acronym}} data into bulk import format.

    :param str output_file: The output filename.
    :param bool debug: Whether debug mode is on.
    """
    click.echo("🚀 Starting the {{cookiecutter.corpus_acronym}} data mapping process.")
    if debug:
        click.echo("📝 Input files:")

    try:
        pass
    except Exception as e:
        click.echo(
            f"❌ Failed to map {{cookiecutter.corpus_acronym}} data to expected JSON. Error: {e}."
        )
        sys.exit(1)

    click.echo("✅ Finished mapping {{cookiecutter.corpus_acronym}} data.")

    click.echo()
    click.echo("🚀 Dumping {{cookiecutter.corpus_acronym}} data to output file")
    click.echo("✅ Finished dumping mapped {{cookiecutter.corpus_acronym}} data.")


if __name__ == "__main__":
    entrypoint()
