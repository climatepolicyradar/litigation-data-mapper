#! /usr/bin/env bash
set -e

# Set the venv name and path for uv
venv_name=".venv"
venv_path="$(pwd)"

# Generate the pyrightconfig.json file.
json_string=$(jq -n \
	--arg v "${venv_name}" \
	--arg vp "${venv_path}" \
	'{
        venv: $v,
        venvPath: $vp,
        include: ["litigation_data_mapper", "tests"],
        exclude: ["**/__pycache__"],
        pythonVersion: "3.10",
        typeCheckingMode: "basic",
        extraPaths: ["."]
    }')

echo "${json_string}" >pyrightconfig.json

# Check whether required keys are present in pyrightconfig.json.
if ! jq -r --arg venv_name "${venv_name}" '. | select((.venv != $venv_name or .venv == "") and (.venvPath == null or .venvPath == ""))' pyrightconfig.json >/dev/null 2>&1; then
	echo "Failed to configure pyright to use environment '${venv_name}' as interpreter. Please check pyrightconfig.json..."
	exit 1
fi

echo "All done! 🦄 Pyright is now configured to use ${venv_name}."
exit 0
