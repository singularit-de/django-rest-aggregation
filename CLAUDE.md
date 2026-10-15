# CLAUDE.md

DRF mixin library (`AggregationMixin`) that adds a `GET …/aggregation/` action to ViewSets.
Published on PyPI as `django-rest-aggregation`, repo `singularit-de/django-rest-aggregation`. Small codebase,
about 300 lines in `src/django_rest_aggregation/`.

## Documentation layout

- `README.md` is only a signpost: short pitch, install, one example, links.
- `Readme/` holds atomic notes, one topic per file, linked to each other. Add new content as a new note
  or into the matching note, and link it from `README.md`.
- `Readme/issues.md` is the backlog of known vulnerabilities, bugs and packaging problems with IDs
  (`SEC-n`, `BUG-n`, `PKG-n`). Reference these IDs in commits and remove or mark entries when fixed.
  Keep the "verified / from code" status honest.
- Docs are in English (public package).

## Commands

```bash
uv sync                                 # creates .venv: package, runtime deps, dev group
uv run runtests.py                      # = manage.py test with tests.settings; args are passed through
uv run coverage run runtests.py && uv run coverage report
uv run ruff check . && uv run ruff format .   # line length 120 (ruff.toml); also runs as pre-commit hook and in CI
uv run ty check                         # type check of src/ ([tool.ty] in pyproject.toml); pre-commit hook and CI
```

- uv only, no pip / `requirements*.txt`. Dependencies are in `pyproject.toml` (`dependencies`, `[dependency-groups]`
  `dev`, `postgres`, `mssql`); `uv.lock` is committed.
- Tests import the installed package (`django_rest_aggregation`, editable via `uv sync`), not `src.`.
- Database: in-memory SQLite by default; `DB_BACKEND=postgres|mysql|mariadb|mssql` plus optional
  `DB_NAME`/`DB_USER`/`DB_PASSWORD`/`DB_HOST`/`DB_PORT` select another one (`tests/settings.py`).
- Test layout: `tests/settings.py`, the test app `tests/testapp/` (models, views, urls, serializers, filters,
  pagination), the shared `setUp` of the filtering and ordering tests in `tests/base.py`, tests in
  `tests/test_<topic>.py`.
- Without `ordering` the row order is not defined (PostgreSQL / SQL Server differ from SQLite). Tests that expect
  several rows pass a total `ordering` on `group_by` fields only; ordering on other fields changes the grouping (BUG-1).

## Typing

All code in `src/` is fully typed, and every new or changed function there must be too:

- Annotate every parameter and return type (ruff `ANN` rules enforce this for `src/`; tests are exempt).
- `uv run ty check` must pass with no diagnostics; do not silence errors with `# type: ignore` / `# ty: ignore`
  unless a third-party gap makes it unavoidable, and then say why in a comment.
- Python 3.10 syntax only (`X | None`, `list[str]`; no `typing.Self`, no PEP 695 generics).
- Imports needed only for annotations go under `if TYPE_CHECKING:` when importing them at runtime has side effects
  or requirements (e.g. `django.contrib.contenttypes`, which needs the app installed).
- Use the existing types instead of re-describing them: `AggregationParams` (parsed query parameters),
  `FilterFields` (`aggregated_filterset_fields`). The mixin is typed against `GenericAPIView` via `_MixinBase`;
  new view attributes it reads get an annotation-only declaration on `AggregationMixin`.
- `py.typed` ships with the package, so the types are part of the public API.

## Code map

- `mixins.py`: `AggregationMixin.aggregation()` runs view filters → `Aggregator` → value filters → ordering
  → pagination → serializer.
- `aggregator.py`: parameter parsing, validation, `.values(*group_by).annotate(name=Agg)`.
- `filter.py`: `ValueFilter` for filters on the aggregated value; the mixin uses a fresh subclass per request
  (`with_filter_fields()`), never mutate `ValueFilter` itself.
- `enums.py`: aggregation names and aliases.
- `serializers.py`: default output serializer, drops fields not in `group_by` / value.

## Things to keep in mind

- The aggregated queryset is a `.values().annotate()` queryset: any `order_by` field outside `group_by`
  becomes part of `GROUP BY` and silently produces wrong results (BUG-1). Test grouping changes with
  ordering applied.
- `group_by` / `aggregation_field` currently expose any model field (SEC-1). Do not widen what is reachable
  without an allowlist; new features must not add new data paths.
- Public API names users rely on: `aggregation_name`, `aggregation_serializer_class`,
  `aggregated_filterset_class`, `aggregated_filterset_fields`, `aggregated_ordering_fields`, the overridable
  methods on the mixin, and the query parameters `aggregation`, `aggregation_field`, `group_by`, `ordering`,
  `<name>__<lookup>`. Renames need deprecation aliases.
- Runtime dependencies are lower bounds only (library, no `~=` pins): Python ≥ 3.10, Django ≥ 5.2, DRF ≥ 3.16,
  django-filter ≥ 25.1 (first releases supporting Django 5.2). Keep `classifiers` in sync when support changes.
  Maintenance priority: SEC-1, BUG-1 (with BUG-3, SEC-2).
- Behaviour changes need a test in the matching `tests/test_<topic>.py` (test app models: `Agent`, `Author`,
  `Book`, `Publisher`, `Store`; ViewSets in `tests/testapp/views.py`).
- CI (`ci.yml`, every push) runs ruff and the tests (Python × Django matrix, PostgreSQL, SQL Server).
- Release: bump `version` in `pyproject.toml`, publish a GitHub release → `publish.yml` runs `ci.yml` on the
  release tag and uploads to PyPI only if it passes. Saving a draft release does not trigger it.
- Commit style: conventional prefixes (`feat:`, `fix:`, `chore:`, `refactor:`, `test:`).
