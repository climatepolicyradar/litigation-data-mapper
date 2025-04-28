# Developer instructions

## Getting started

Pyright requires a bit of gentle massaging before it will start working with
any virtual environment (and therefore with Trunk.io and our pre-commits).

### Setup

Run the makefile command for setting up the environment with uv below:

```bash
make setup_with_uv
```

Commit the changes if the makefile command ran successfully.

### uv

- Create your virtual environment using uv.

```bash
uv venv .venv
source .venv/bin/activate
```

Run the following command if you see the following warning:
_'VIRTUAL_ENV=.venv` does not match the project environment path and will be ignored'_

```bash
export VIRTUAL_ENV="$(pwd)/.venv"
```

- Assuming there is no 'venv' key in the pyright section of your [pyproject.toml](pyproject.toml)
  file, the first time you commit something Trunk.io will run its `pyright`
  action to make sure that pyright is correctly configured with your virtual
  environment with its default setting of uv as the virtual environment
  management method.
