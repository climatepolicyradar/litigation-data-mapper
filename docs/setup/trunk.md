# Trunk.io

## Getting started

1. Run `make share_trunk` to share your Trunk config with version control
2. Make sure `hadolint` is disabled in the [trunk.yaml](.trunk/trunk.yaml) file.
   If it is not, you can run `trunk check disable hadolint` to permanently disable
   hadolint until we have found a resolution to it running slowly/hanging on Mac.

## Custom linters

```yaml
lint:
  definitions:
    - name: bandit
      direct_configs: [bandit.yaml]
      commands:
        - name: lint
          run: bandit --exit-zero -c bandit.yaml --format json --output ${tmpfile} ${target}
```

## Disabling linters

How to disable linters (all or just specific linters) for a selection of files/
folders.

```yaml
lint:
  disabled:
    # Hadolint seems to have excessive memory use on Mac.
    # Disable until we can investigate further.
    - hadolint
```

## Excluding certain files/directories from linting

```yaml
lint:

  ignore:
    - linters: [ALL]
    paths:
        - tests/data/**/*.json # Ignore all JSON files under /tests/data folder recursively
        - tests/search/**/*
        - scripts/**
    - linters: [cspell]
      paths:
        - .trunk/configs/cspell.json # Ignore only a specific file
```
