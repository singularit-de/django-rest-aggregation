# Development

## Setup

```bash
uv sync                      # package (editable) + runtime deps + dev group (coverage, ruff, ty, type stubs, pre-commit)
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
| `tests/testapp/` | Test app: models `Agent`, `Author`, `Book`, `Publisher`, `Store`, five ViewSets that cover the features, their urls, serializers, filters and pagination |
| `tests/base.py` | `FilteringAndOrderingTestCase`: the `setUp` shared by the filtering and ordering tests |
| `tests/test_aggregations.py` | Aggregation functions on number and date fields |
| `tests/test_grouping.py` | `group_by` on fields, relations and annotations |
| `tests/test_validation.py` | Error responses for invalid parameters |
| `tests/test_filtering.py` | View filters before and value filters after aggregation |
| `tests/test_ordering.py` | `ordering` on the aggregated result |
| `tests/test_customization.py` | Custom name, serializer, pagination |
| `tests/test_security.py` | Field allowlist, ordering restricted to result columns, `group_by` limit |

Without `ordering` the row order of an aggregation is not defined: SQLite happens to return rows sorted by the
group columns, PostgreSQL and SQL Server need not. Every test that expects several rows therefore passes an
`ordering` that fixes the order completely, using `group_by` fields only (ordering on other fields adds them to
`GROUP BY` and changes the result; the package ignores such terms, see [Ordering](ordering.md)).

Known weak spots, to be reworked later:

- Fixtures are created per test in `setUp` and URLs are hard-coded (`/book/aggregation/`).

State on 2026-10-15: all 37 tests pass on Python 3.14 with Django 6.1.2, DRF 3.18.3, django-filter 26.2
(SQLite 3.46), also with `--shuffle`, `--reverse` and `-W error::DeprecationWarning`. CI runs the other
combinations.

### CI

`.github/workflows/ci.yml` runs on every push to any branch (and manually via `workflow_dispatch`):

- `test`: Python 3.10–3.14 × Django 5.2 / 6.0 / 6.1 (Django 6.x only on 3.12+) on SQLite, with
  `-W error::DeprecationWarning` so Django deprecations fail early.
- `test-postgres`: lowest and latest combination against a PostgreSQL 17 service.
- `test-mssql`: the same two combinations against a SQL Server 2022 service. The test settings use
  mssql-django's `mssql_python` driver, which ships ODBC Driver 18, so no system ODBC packages are needed.

## Lint and type check

```bash
uv run ruff check . && uv run ruff format --check .
uv run ty check
```

Config: `ruff.toml` (line length 120, explicit rule selection so ruff upgrades do not change the checks) and
`[tool.ty]` in `pyproject.toml`.

The package in `src/` is fully typed and ships a `py.typed` marker. ruff's `ANN` rules require annotations
for every function in `src/` (`tests/` is exempt), and [ty](https://docs.astral.sh/ty/) checks that the types
are correct; it only checks `src/`. The rules for new code are in `CLAUDE.md` (section "Typing").

Ruff and ty run in two places, both with the versions pinned in `uv.lock`:

- **pre-commit hook** (`.pre-commit-config.yaml`): fixes and formats staged files and aborts the commit
  if it changed anything, then runs `ty check`; review and stage the changes, then commit again.
  `uv run pre-commit run --all-files` checks the whole repo.
- **CI** (`.github/workflows/ci.yml`, job `Ruff`): runs `ruff check`, `ruff format --check` and `ty check` on every
  push. It also fails if `uv.lock` is out of date (`uv sync --locked`).

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
