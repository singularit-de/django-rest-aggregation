# Development

## Setup

```bash
uv venv
uv pip install -r requirements-dev.txt   # includes mssql-django, which needs ODBC headers
# or only what the tests need:
uv pip install -r requirements.txt
```

## Tests

```bash
python runtests.py
```

- Uses Django's test runner with `tests.settings`; there is no pytest.
- Default database is SQLite (`db.sqlite3` in the repo root). `tests/settings.py` also has
  PostgreSQL, MySQL, MariaDB and MSSQL configs; switch `DATABASES["default"]` to use one.
- The test app (`tests/`) has models `Agent`, `Author`, `Book`, `Store` and four ViewSets
  that cover the features; `tests/test_aggregation.py` holds all 25 tests.
- `tests/views.py` imports `src.django_rest_aggregation`, so run tests from the repo root.

State on 2026-10-15 (SQLite 3.46, Python 3.14): 23 of 25 tests pass with
Django 4.2.30 / DRF 3.17.2 / django-filter 23.5 and with Django 5.2.18 / DRF 3.18.3 / django-filter 26.2. `test_sum` and `test_avg` fail on exact float comparisons
([BUG-14](issues.md#bug-14-two-tests-fail-on-exact-float-comparison)).

## Lint

```bash
ruff check . && ruff format --check .
```

Config: `ruff.toml` (line length 120).

## Release

1. Bump `version` in `pyproject.toml`.
2. Create a GitHub release. `.github/workflows/publish.yml` builds and uploads to PyPI with
   trusted publishing (environment `pypi`).

No workflow runs the tests ([PKG-4](issues.md#pkg-4-no-ci-for-tests)).

Related: [Architecture](architecture.md) · [Issues](issues.md)
