# Climate Policy Radar Data Mapper template repository

A cookiecutter template for data mapper projects.

## Getting started

All repositories using cookiecutter use python 3.10. You will need [cookiecutter](https://cookiecutter.readthedocs.io/en/latest/installation.html)
(available via brew and pip) installed too.

1. Kick off cookiecutter against this template repo (run this command from
   the folder containing all your git repo checkouts)

    ```bash
    cookiecutter https://github.com/climatepolicyradar/data-mapper-template.git
    ```

2. This will prompt you to enter a bunch of project config values (defined in
   the project’s [cookiecutter.json](cookiecutter.json))

3. Navigate to the new folder on your machine that contains your new project

   ```bash
   cd {{cookiecutter.repo_name}}
   ```

4. Run the setup

    ```bash
    make setup
    ```

5. Commit and push all changes to the remote

    ```bash
    git commit -anm "Initial commit of {{ cookiecutter.project_name }}"
    git push
    ```

## Developing this repo

Run `make setup` to install pre-commit and the pre-commit hooks that run on the
built cookiecutter template. This will prevent you from pushing code that
doesn't pass CI checks.

## Acknowledgements

This project structure is based on our data scientist's [experiment-template](https://github.com/climatepolicyradar/experiment-template)
repo.
