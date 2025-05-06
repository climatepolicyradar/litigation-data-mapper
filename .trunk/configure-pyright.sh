#! /usr/bin/env bash
set -e

# Set the venv name and path for uv/standard venvs
venv_name=".venv"
venv_path="$(pwd)"

# Generate the pyrightconfig.json file.
jq -n \
	--arg v "${venv_name}" \
	--arg vp "${venv_path}" \
	'{venv: $v, venvPath: $vp}' >pyrightconfig.json

echo "All done! 🦄 Pyright is now configured to use .venv."
exit 0
