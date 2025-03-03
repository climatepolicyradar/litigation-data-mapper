# Developer instructions

## Getting started

Pyright requires a bit of gentle massaging before it will start working with
any virtual environment (and therefore with Trunk.io and our pre-commits).
Please follow the set up instructions in the sub-heading specific to which tool
you use to manage your virtual environments (Poetry and Pyenv only supported).

### Pyenv

Run the makefile command for setting up the environment with Pyenv below:

```bash
make setup_with_pyenv
```

Commit the changes if the makefile command ran successfully.

### Poetry

- Create your virtual environment using Poetry.
- Assuming there is no 'venv' key in the pyright section of your [pyproject.toml](pyproject.toml)
  file, the first time you commit something Trunk.io will run its `pyright`
  action to make sure that pyright is correctly configured with your virtual
  environment with it's default setting of Poetry as the virtual environment
  management method.
