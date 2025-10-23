# LITIGATION Data Mapper

A CLI tool to map the litigation data to the required JSON format for
bulk-import.

- _Developers_ please read the [developers.md](docs/setup/developers.md) file
  for more information.

- This tool is designed to map litigation data as received from the Sabin API

make build # Ensure you have the package built

## Install the package into your environment

```bash
uv run pip install dist/litigation-data-mapper-<version>-py3-none-any.whl
```

## Usage

The mapper can be run locally as a CLI tool by navigating to the
litigation_data_mapper directory and running:

```bash
litigation_data_mapper
```

If `--output_file` is not passed, by default an output file called `output.json`
will be created in the current directory if it does not already exist.

```bash
litigation_data_mapper --output_file FILENAME
```

By default the command will fetch all data from the Sabin API. Setting the
`--get-modified-data` flag to true will fetch only data that was added/modified
in the update window specified (currently last 24hrs).

This tool is also run as a
[scheduled Prefect flow](https://app.prefect.cloud/account/4b1558a0-3c61-4849-8b18-3e97e0516d78/workspace/1753b4f0-6221-4f6a-9233-b146518b4545/deployments?deployments.flowOrDeploymentNameLike=litigation)
which pulls any new or updated data from the Sabin API and automatically passes
them to the admin service backend /bulk-import endpoint to import to the RDS
database.
