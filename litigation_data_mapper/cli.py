import os
import sys

import click


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
    if debug:
        click.echo("📝 Input files:")

    try:
        pass
    except Exception as e:
        click.echo(f"❌ Failed to map litigation data to expected JSON. Error: {e}.")
        sys.exit(1)

    click.echo("✅ Finished mapping litigation data.")

    click.echo()
    click.echo("🚀 Dumping litigation data to output file")
    click.echo("✅ Finished dumping mapped litigation data.")


if __name__ == "__main__":
    entrypoint()
