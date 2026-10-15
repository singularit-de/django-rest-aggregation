# Development

## Setup

```bash
uv sync                      # package (editable) + runtime deps + dev group (coverage, ruff, pre-commit)
uv run pre-commit install    # ruff check --fix and ruff format before every commit
uv sync --group postgres     # adds psycopg2-binary
uv sync --group mssql        # adds mssql-django (tests use its bundled mssql-python driver)
```

Dependencies live in `pyproject.toml` (`[project.dependencies]` and `[dependency-groups]`);
`uv.lock` is committed. Update it with `uv lock --upgrade`.

## Tests

```bash
uv run runtests.py                                   # whole suite
uv run runtests.py tests.test_validation --failfast   # one module, class or test
uv run runtests.py --shuffle                         # any `manage.py test` option works
uv run coverage run runtests.py && uv run coverage report
```

- `runtests.py` runs `manage.py test` with `tests.settings`; there is no pytest.
- Tests import the installed package `django_rest_aggregation` (editable install from `uv sync`).
- Database: in-memory SQLite by default. Set `DB_BACKEND` to `postgres`, `mysql`, `mariadb` or `mssql`
  to use another backend; `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` and `DB_PORT` override the
  connection defaults in `tests/settings.py`:

  ```bash
  DB_BACKEND=postgres uv run --group postgres runtests.py
  ```

Layout:

| Path | Contents |
|------|----------|
| `tests/settings.py` | Test project settings, database selection |
| `tests/testapp/` | Test app: models `Agent`, `Author`, `Book`, `Store`, four ViewSets that cover the features, their urls, serializers, filters and pagination |
| `tests/base.py` | `FilteringAndOrderingTestCase`: the `setUp` shared by the filtering and ordering tests |
| `tests/test_aggregations.py` | Aggregation functions on number and date fields |
| `tests/test_grouping.py` | `group_by` on fields, relations and annotations |
| `tests/test_validation.py` | Error responses for invalid parameters |
| `tests/test_filtering.py` | View filters before and value filters after aggregation |
| `tests/test_ordering.py` | `ordering` on the aggregated result |
| `tests/test_customization.py` | Custom name, serializer, pagination |

Known weak spots, to be reworked later:

- Several tests compare result lists in a fixed order although the request has no total `ordering`
  (e.g. plain `group_by`). SQLite happens to return a stable order; PostgreSQL and SQL Server need not, so these
  tests may fail there.
- Fixtures are created per test in `setUp` and URLs are hard-coded (`/book/aggregation/`).

State on 2026-10-15: all 25 tests pass on Python 3.14 with Django 6.1.2, DRF 3.18.3, django-filter 26.2
(SQLite 3.46), also with `--shuffle`, `--reverse` and `-W error::DeprecationWarning`. CI runs the other
combinations.

### CI

`.github/workflows/ci.yml` runs on every push to any branch (and manually via `workflow_dispatch`):

- `test`: Python 3.10–3.14 × Django 5.2 / 6.0 / 6.1 (Django 6.x only on 3.12+) on SQLite, with
  `-W error::DeprecationWarning` so Django deprecations fail early.
- `test-postgres`: lowest and latest combination against a PostgreSQL 17 service.
- `test-mssql`: the same two combinations against a SQL Server 2022 service. The test settings use
  mssql-django's `mssql_python` driver, which ships ODBC Driver 18, so no system ODBC packages are needed.

## Lint

```bash
uv run ruff check . && uv run ruff format --check .
```

Config: `ruff.toml` (line length 120, explicit rule selection so ruff upgrades do not change the checks).

Ruff runs in two places, both with the version pinned in `uv.lock`:

- **pre-commit hook** (`.pre-commit-config.yaml`): fixes and formats staged files and aborts the commit
  if it changed anything; review and stage the changes, then commit again.
  `uv run pre-commit run --all-files` checks the whole repo.
- **CI** (`.github/workflows/ci.yml`, job `Ruff`): runs `ruff check` and `ruff format --check` on every push.
  It also fails if `uv.lock` is out of date (`uv sync --locked`).

Test other versions without touching `.venv`:

```bash
uv run --isolated --python 3.10 --resolution lowest-direct runtests.py   # lowest supported versions (no CI job)
uv run --isolated --with "django<6" runtests.py                          # Django 5.2
```

## Release

1. Bump `version` in `pyproject.toml`.
2. Run `uv lock` so the lock file picks up the new version.
3. Publish a GitHub release. `.github/workflows/publish.yml` first runs the whole `ci.yml` (lint and all test
   jobs) on the release tag. Only if it passes does it build with `uv build` and upload to PyPI with trusted
   publishing (environment `pypi`).

The workflow triggers on `release: published`, so saving a draft release does not upload anything. If CI
fails, fix the problem, then delete and recreate the release and tag, since PyPI does not accept the same
version twice and the failed run uploaded nothing.

Related: [Architecture](architecture.md) · [Issues](issues.md)
