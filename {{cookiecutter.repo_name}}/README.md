# {{ cookiecutter.project_name }}

A CLI tool to map the {{ cookiecutter.corpus_acronym }} data to the required JSON format for bulk-import.

- _Developers_ please read the [developers.md](docs/setup/developers.md) file for more
  information.

- This tool is designed to map this {{ cookiecutter.corpus_acronym }} data

## Installation

This package is not available on PyPI. To install it, you need to build the
package and install it locally.

```bash
make build # Ensure you have the package built

# Install the package into your environment
poetry run pip install dist/{{cookiecutter.repo_name}}-<version>-py3-none-any.whl
```

Goto the [releases page](https://github.com/climatepolicyradar/{{cookiecutter.package_name}}/releases)
to find the latest version.

## Usage

If `--output_file` is not passed, by default an output file called `output.json`
will be created in the current directory if it does not already exist.

```bash
{{cookiecutter.repo_name}} --output_file FILENAME
```
