# HousePy

A FastAPI service for modeling European nobility family trees — tracking people, titles, and lineage events through a graph-backed data model.

## Overview

HousePy models European noble houses using:

- **Person** — individuals with name, birth, and death data
- **Family** — household/dynastic groupings
- **Title** — Regnal or Peerage titles, with creation/ascension and optional descent events
- **Event** — dated occurrences (birth, death, ascension, etc.) with optional place
- **Repository** — a `NetworkX`-backed graph linking people and families through shared titles and parent-child relationships

### Slug conventions

Every `Person`, `Title`, and `Family` has a `slug` — a unique, human-readable
identifier used as its API id and URL path segment. These are hand-authored,
not generated, and follow documented conventions rather than validated
rules — uniqueness and format are on you when adding data:

- **Person** — `house.identifier`, e.g. `hesse-darmstadt.ludwig-i`
- **Title** — `realm.office`, e.g. `hesse-darmstadt.landgrave`, `england.king`
  (territorial/institutional, independent of whichever house holds it)
- **Family** — `{father}+{mother}+family-N`, omitting whichever parent is
  unknown (e.g. `{father}+family-1`); if both are unknown, anchor on a known
  child instead, or fall back to a bare `family-N`. `N` disambiguates
  multiple families sharing the same known parent(s).

## Requirements

- Python ^3.14
- [Poetry](https://python-poetry.org/) for dependency management

## Installation

```bash
git clone https://github.com/nickwhitt/housepy.git
cd housepy
poetry install
```

## Project Structure

```
housepy/
├── src/
│   └── housepy/
│       ├── __init__.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── name.py
│       │   ├── event.py
│       │   └── ...
│       └── api/
│           └── ...
├── tests/
│   └── models/
│       └── ...
├── pyproject.toml
└── README.md
```

Internal imports use full package paths, e.g.:

```python
from housepy.models.name import Name
```

## Development

Install in editable mode (handled automatically by `poetry install`):

```bash
poetry install
```

Run the test suite:

```bash
poetry run pytest
```

### Editor Setup (VS Code)

This repo ships a `.vscode/settings.json` and `.vscode/extensions.json` with recommended tooling. When you open the folder, VS Code will prompt you to install:

- **Python** + **Pylance** — interpreter/environment detection, IntelliSense, and `src`-layout import resolution
- **Ruff** — linting, formatting, and import sorting (replaces black + isort + flake8)
- **Even Better TOML** — schema-aware editing/validation for `pyproject.toml` and `poetry.lock`

Format-on-save and lint auto-fixes are preconfigured for Python files. None of this is required to build or run the project — it's editor convenience only, and settings for uninstalled extensions are simply ignored.

## Running the API

```bash
poetry run uvicorn housepy.main:app --reload
```

## License

- **Code** — [MIT](LICENSE)
- **Data** — [CC BY 4.0](DATA_LICENSE.md)

The HousePy codebase (models, API, tooling) is MIT-licensed. The genealogical dataset it ships with or generates — people, titles, families, and events — is licensed separately under **Creative Commons Attribution 4.0 International**, so it can be freely reused, adapted, and redistributed by researchers and other projects, provided HousePy is credited as the source. See [DATA_LICENSE.md](DATA_LICENSE.md) for the full terms and attribution guidance, and [CITATION.cff](CITATION.cff) for how to cite the project itself.
