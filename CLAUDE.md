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
uv run runtests.py                      # Django test runner, settings: tests.settings, SQLite by default
uv run ruff check . && uv run ruff format .   # line length 120 (ruff.toml)
```

- uv only, no pip / `requirements*.txt`. Dependencies are in `pyproject.toml` (`dependencies`, `[dependency-groups]`
  `dev`, `postgres`, `mssql`); `uv.lock` is committed.
- Run tests from the repo root: `tests/views.py` imports `src.django_rest_aggregation` (PKG-3).
- `test_sum` and `test_avg` currently fail on exact float comparison (BUG-14); everything else passes on
  Django 4.2, 5.2 and 6.1.
- `runtests.py` writes `db.sqlite3` into the repo root; it is gitignored.

## Code map

- `mixins.py`: `AggregationMixin.aggregation()` runs view filters → `Aggregator` → value filters → ordering
  → pagination → serializer.
- `aggregator.py`: parameter parsing, validation, `.values(*group_by).annotate(name=Agg)`.
- `filter.py`: `ValueFilter` for filters on the aggregated value. **It mutates class state** (BUG-2).
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
- Runtime dependencies are lower bounds only (library, no `~=` pins). Python ≥ 3.8 and Django 4.2 are still
  allowed, both EOL (PKG-2). Maintenance priority: PKG-2, PKG-4, then SEC-1, BUG-1, BUG-2.
- Behaviour changes need a test in `tests/test_aggregation.py` (test app models: `Agent`, `Author`, `Book`,
  `Store`; ViewSets in `tests/views.py`).
- Release: bump `version` in `pyproject.toml`, create a GitHub release → `publish.yml` uploads to PyPI.
  There is no test CI yet, so run tests locally before releasing.
- Commit style: conventional prefixes (`feat:`, `fix:`, `chore:`, `refactor:`, `test:`).
