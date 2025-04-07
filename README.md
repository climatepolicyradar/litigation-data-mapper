# LITIGATION Data Mapper

A CLI tool to map the litigation data to the required JSON format for bulk-import.

- _Developers_ please read the [developers.md](docs/setup/developers.md) file
  for more information.

- This tool is designed to map this litigation data

## Installation

This package is not available on PyPI. To install it, you need to build the
package and install it locally.

```bash
make build # Ensure you have the package built

# Install the package into your environment
poetry run pip install dist/litigation-data-mapper-<version>-py3-none-any.whl
```

Goto the [releases page](https://github.com/climatepolicyradar/litigation-data-mapper/releases)
to find the latest version.

## Usage

If `--output_file` is not passed, by default an output file called `output.json`
will be created in the current directory if it does not already exist.

```bash
litigation-data-mapper --output_file FILENAME
```

The `--use-cache` option will use the cached data if it exists. This is useful for
testing purposes. The cache is stored in the `litigation_raw_output.json` file.
If the cache does not exist, it will be created. Note that by default the cache
is not used.
