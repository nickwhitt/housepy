# HousePy

[![Release](https://img.shields.io/github/v/release/nickwhitt/housepy)](https://github.com/nickwhitt/housepy/releases)
[![CI](https://github.com/nickwhitt/housepy/actions/workflows/ci.yml/badge.svg)](https://github.com/nickwhitt/housepy/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.14+](https://img.shields.io/badge/python-3.14%2B-blue.svg)](pyproject.toml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21866352.svg)](https://doi.org/10.5281/zenodo.21866352)

A FastAPI service for modeling European nobility family trees — tracking people, titles, and lineage events through a graph-backed data model.

**[Live API](https://housepy.fastapicloud.dev)** · **[Docs & family tree graph](https://nickwhitt.github.io/housepy/)**

## Overview

HousePy models European noble houses using:

- **Person** — individuals with name, birth, and death data, an optional
  current `house` and `birth_house` (when it differs — e.g. a house rename
  partway through life), and an optional `sex` (`male`/`female`; unset means
  not recorded)
- **Family** — household/dynastic groupings
- **Title** — Regnal or Peerage titles, with tenure start/end/ceremony events
  per holder, plus `created`/`abolished` events dating the office itself
  (independent of any one holder's tenure — e.g. an office superseded by a
  new one, distinct from its last holder's own tenure ending)
- **House** — a dynasty/noble house, with optional parent house (cadet
  branches), founder, founding event, and `renamed_from` (for the same
  house/institution continuing under a new name, e.g. Saxe-Coburg and
  Gotha → Windsor)
- **Event** — dated occurrences (birth, death, ascension, etc.) with optional place

These four are exposed as JSON:API resources (`Person`/`Title`/`Family`/`House`
— `Event` is an attribute of the others, not a resource of its own). The same
data also drives a separate, static
[NetworkX](https://networkx.org/)/[pyvis](https://pyvis.readthedocs.io/) graph
linking people, titles, and families — see **Documentation site** below.

### Slug conventions

Every `Person`, `Title`, `Family`, and `House` has a `slug` — a unique,
human-readable identifier used as its API id and URL path segment. These
are hand-authored, not generated, and follow documented conventions rather
than validated rules — uniqueness and format are on you when adding data:

- **Person** — `house.identifier`, e.g. `hesse-darmstadt.ludwig-i`
- **Title** — `realm.office`, e.g. `hesse-darmstadt.landgrave`, `england.king`
  (territorial/institutional, independent of whichever house holds it)
- **Family** — `{father}+{mother}+family-N`, omitting whichever parent is
  unknown (e.g. `{father}+family-1`); if both are unknown, anchor on a known
  child instead, or fall back to a bare `family-N`. `N` disambiguates
  multiple families sharing the same known parent(s).
- **House** — a bare identifier, e.g. `hesse-darmstadt`, `saxe-coburg-and-gotha`
  (this is the root of the `house.identifier` convention Person/Title slugs
  build on, so it needs no compound form of its own)

### Editing the dataset

The dataset lives in [`src/housepy/db/seed.sql`](src/housepy/db/seed.sql) — a
plain-text SQL dump of the seed data (just `INSERT`s) that's the single
committed source of truth for content; the schema itself is defined in
[`src/housepy/db/tables.py`](src/housepy/db/tables.py) as SQLAlchemy models.
The app builds the schema and loads the seed data into an in-memory SQLite
database on startup; it's never a live, persisted datastore.

To add or edit records:

1. `poetry run python scripts/build_db.py` — builds a local `housepy.db`
   from `seed.sql`.
2. Open `housepy.db` in a GUI tool such as
   [DB Browser for SQLite](https://sqlitebrowser.org/) and make your changes.
   Foreign key and required-field constraints are enforced live, so a bad
   slug reference or missing field is rejected immediately, the same way a
   type checker would catch it in code.
3. `poetry run python scripts/dump_db.py` — regenerates `seed.sql` from your
   edits (it aborts if `PRAGMA foreign_key_check` finds anything broken).
   Review the diff and commit it.

`events` rows also need a hand-authored slug — it's a database-only key (not
an API id or URL segment, since `Event` isn't its own resource) used just to
keep `birth_event_slug`/`start_event_slug`/etc. foreign keys readable in a
diff. Convention: `{owning-slug}+{role}`, e.g.
`hesse-darmstadt.ludwig-i+birth`, `hesse-darmstadt+founded`; for a title
tenure's start/end/ceremony, `{person.slug}+{title.slug}+{role}`, e.g.
`hesse-darmstadt.ludwig-i+hesse-darmstadt.landgrave+start`.

`housepy.db` itself is gitignored — it's a disposable local working copy,
not something to commit.

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

With a coverage report:

```bash
poetry run pytest --cov=housepy --cov-report=term-missing
```

Type-check with [pyright](https://microsoft.github.io/pyright/):

```bash
poetry run pyright
```

### Editor Setup (VS Code)

This repo ships a `.vscode/settings.json` and `.vscode/extensions.json` with recommended tooling. When you open the folder, VS Code will prompt you to install:

- **Python** + **Pylance** — interpreter/environment detection, IntelliSense, and `src`-layout import resolution
- **Ruff** — linting, formatting, and import sorting (replaces black + isort + flake8)
- **Even Better TOML** — schema-aware editing/validation for `pyproject.toml` and `poetry.lock`

Format-on-save and lint auto-fixes are preconfigured for Python files. None of this is required to build or run the project — it's editor convenience only, and settings for uninstalled extensions are simply ignored.

## Running the API

A live instance runs at **[housepy.fastapicloud.dev](https://housepy.fastapicloud.dev)**,
auto-deployed from `main` on every push. To run locally instead:

```bash
poetry run fastapi dev
```

Routes are versioned under `/v1` (e.g. `GET /v1/people`, not `GET /people`).
Responses follow the [JSON:API](https://jsonapi.org/) spec:

- List endpoints support `page[number]`/`page[size]` pagination (default page
  size 20, capped at 100) and return `first`/`prev`/`next`/`last` links.
- Errors — 404s, validation failures, etc. — come back as a JSON:API error
  document (`{"errors": [{"status", "title", "detail"}, ...]}`), not FastAPI's
  default `{"detail": ...}` shape.
- `GET /` is a self-discovery document linking to each resource collection
  plus the Swagger, Redoc, and OpenAPI schema URLs.

Interactive API docs are available at `/docs` (Swagger) and `/redoc` (Redoc)
once the server is running.

## Documentation site

Published at **[nickwhitt.github.io/housepy](https://nickwhitt.github.io/housepy/)**
from the [`docs/`](docs/) folder on every push to `main`: a static Redoc export of the
API schema, and an interactive
[pyvis](https://pyvis.readthedocs.io/)/[NetworkX](https://networkx.org/)
family-tree graph (`docs/graph.html`) linking people, titles, and families.
Person nodes are colored by house (each house's color traced back to its
root house, so cadet branches share a color with their parent) and shaped by
`sex` (square/rounded-box corners, diamond when unset); clicking a node
highlights its immediate family/title neighborhood and dims the rest,
clicking empty canvas resets it. Both files are generated fresh at deploy
time (`scripts/export_openapi.py`, `scripts/export_graph.py`) — neither is
committed.

## Contributing

Both code and dataset changes (see **Editing the dataset** above) go through
pull requests. Before opening one, run:

```bash
poetry run ruff check .
poetry run ruff format .
poetry run pytest
poetry run pyright
```

CI runs the same checks on every push and PR.

## License

- **Code** — [MIT](LICENSE)
- **Data** — [CC BY 4.0](DATA_LICENSE.md)

The HousePy codebase (models, API, tooling) is MIT-licensed. The genealogical dataset it ships with or generates — people, titles, families, and events — is licensed separately under **Creative Commons Attribution 4.0 International**, so it can be freely reused, adapted, and redistributed by researchers and other projects, provided HousePy is credited as the source. See [DATA_LICENSE.md](DATA_LICENSE.md) for the full terms and attribution guidance, and [CITATION.cff](CITATION.cff) for how to cite the project itself.
