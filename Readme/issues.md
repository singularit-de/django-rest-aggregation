# Issues: vulnerabilities, bugs, optimizations

Review of v0.4.0 (commit `20df1d3`), 2026-10-15.

**Verified** = reproduced against the test app on Django 5.2.18 with a probe script.
**From code** = read from the source, not run.

## Overview

| ID | Severity | Topic | Status |
|----|----------|-------|--------|
| [SEC-1](#sec-1-any-model-field-can-be-read-through-group_by-and-aggregation_field) | high | Data exposure via `group_by` / `aggregation_field` | **fixed** |
| [SEC-2](#sec-2-ordering-is-permissive-by-default) | medium | Ordering on any field by default | **fixed** |
| [SEC-3](#sec-3-no-limit-on-query-cost) | medium | No limit on query cost | **fixed** |
| [BUG-1](#bug-1-ordering-by-a-non-grouped-field-breaks-the-aggregation) | high | Ordering breaks `GROUP BY`, wrong results | **fixed** |
| [BUG-2](#bug-2-valuefilter-is-shared-mutable-state) | high | `ValueFilter` is shared mutable state | **fixed** |
| [BUG-3](#bug-3-unknown-ordering-field-returns-500) | medium | Unknown ordering field → 500 | **fixed** |
| [BUG-4](#bug-4-count-assumes-a-primary-key-named-id) | medium | `count` assumes pk named `id` | **fixed** |
| [BUG-5](#bug-5-numeric-type-check-is-too-narrow) | medium | Numeric type check too narrow | partly fixed |
| [BUG-6](#bug-6-value-filters-are-always-numberfilter) | low | Value filters only numeric | verified |
| [BUG-7](#bug-7-count-on-an-empty-queryset-returns-an-empty-list) | low | Empty queryset → `[]` | verified |
| [BUG-8](#bug-8-group_by-whitespace-is-not-stripped) | low | `group_by` whitespace | **fixed** |
| [BUG-9](#bug-9-the-magic-group-annotation) | low | Magic `group` annotation | from code |
| [BUG-10](#bug-10-string-ordering_fields-match-substrings) | low | String `ordering_fields` match substrings | **fixed** |
| [BUG-11](#bug-11-translated-aggregation-names) | low | Translated aggregation names | from code |
| [BUG-12](#bug-12-annotation-type-lookup-can-raise) | low | Annotation type lookup can raise | **fixed** |
| [BUG-13](#bug-13-serializer-re-parses-group_by) | low | Serializer re-parses `group_by` | from code |
| [BUG-14](#bug-14-two-tests-fail-on-exact-float-comparison) | low | Two tests fail | **fixed** |
| [PKG-1](#pkg-1-runtime-dependencies-are-not-declared) | high | Dependencies not declared | **fixed** |
| [PKG-2](#pkg-2-supported-versions-are-out-of-date) | high | Django 4.2 / Python 3.8 are EOL | **fixed** |
| [PKG-3](#pkg-3-tests-import-from-src) | low | Tests import `src.` | **fixed** |
| [PKG-4](#pkg-4-no-ci-for-tests) | medium | No test CI | **fixed** |
| [PKG-5](#pkg-5-packaging-metadata-and-tooling) | low | Metadata and tooling | **fixed** |
| [PKG-6](#pkg-6-readme-links-on-pypi) | low | Relative README links on PyPI | – |
| [OPT](#optimizations-and-ideas) | – | Optimizations and ideas | – |

---

## SEC-1 Any model field can be read through `group_by` and `aggregation_field`

`group_by` and `aggregation_field` accept every model field and every relation path
(`aggregator.py:46-62`). Nothing ties them to the view's serializer, so an endpoint
that hides a field in its normal API still returns it through aggregation.

Verified: the test `Book` API does not expose agents, yet
`/book/aggregation/?aggregation=count&group_by=author__agent__address` returns
`[{"author__agent__address": "Secret Street 1", "value": 2}, …]`.
`aggregation=max&aggregation_field=author__age` reads related values the same way.
On a user model this could expose `password` hashes, emails or tokens through `group_by=user__password`.

**Fixed:** one allowlist, `aggregation_fields`, for both parameters. The default is the readable fields of the
view's serializer (`source` with `.` as `__`); `"__all__"` restores the old behaviour. Disallowed fields get the
same 400 as unknown ones. **Breaking change:** relation paths not exposed by the serializer now need to be
listed; release as 0.5. See [Field access](field-access.md). Tests: `tests/test_security.py`.

## SEC-2 Ordering is permissive by default

If neither `aggregated_ordering_fields` nor `ordering_fields` is set, any `ordering` term is
applied (`mixins.py:65`). Ordering by hidden or related fields lets clients infer their values
(an ordering oracle), and unknown names cause a 500 (BUG-3).

**Fixed:** `ordering` only accepts result columns (`group_by` fields, the aggregation name, `group`), read from
the aggregated queryset; other terms are dropped. `aggregated_ordering_fields` / `ordering_fields` can only
narrow this further. Tests: `test_ordering_by_non_grouped_field_keeps_grouping`,
`test_ordering_by_non_grouped_field_is_ignored`.

## SEC-3 No limit on query cost

There is no limit on the number of `group_by` fields or on relation depth. Paths over several
ManyToMany relations produce large joins and group counts. Without pagination the full result is returned.

**Fixed:** `aggregation_max_group_by` (default 3, `None` for no limit) caps the number of group fields.
Relation depth is capped by the allowlist from SEC-1 instead of a separate setting: only listed or
serializer-exposed paths work. The docs recommend pagination ([Field access](field-access.md)).
Test: `test_group_by_field_limit`.

## BUG-1 Ordering by a non-grouped field breaks the aggregation

Django adds `order_by()` fields to `GROUP BY` on a `.values().annotate()` queryset. Two paths lead there:

1. `order_aggregated_queryset()` applies terms that are not in `group_by` (`mixins.py:52-60`).
2. `OrderingFilter` already ordered the model queryset in `filter_queryset()` (`mixins.py:13`).
   If the post-aggregation allowlist drops every term, that earlier ordering stays.

Verified, both paths: `/book/aggregation/?aggregation=count&group_by=author&ordering=name`
returns `[{author:1, value:1}, {author:1, value:1}, {author:2, value:1}]` instead of
`[{author:1, value:2}, {author:2, value:1}]`. The same happens with `aggregated_ordering_fields = ["value"]`.

**Fixed:** `get_aggregated_queryset()` calls `order_by()` before `.values()`, and `ordering` only accepts result
columns (SEC-2). Test: `test_ordering_by_non_grouped_field_keeps_grouping` (covers both paths).

## BUG-2 `ValueFilter` is shared mutable state

`ValueFilter.set_filter_fields()` writes into `ValueFilter.base_filters`, a class attribute
(`filter.py:23-29`), on every request of a view with `aggregated_filterset_fields`. All views that use
the default `ValueFilter` share these filters, and they pile up for every `aggregation_name` used.

Verified: after one request to `customized_book`, `ValueFilter.base_filters` holds both `value__*` and
`CustomizedValue__*`, and `/store/aggregation/?aggregation=count&CustomizedValue__gt=0` returns 500
(`Store` has no `CustomizedValue` annotation). Behaviour depends on request order, and concurrent
requests mutate the same dict.

**Fixed:** the mixin builds a fresh subclass per request with `ValueFilter.with_filter_fields()` and no longer
touches `ValueFilter` itself. `set_filter_fields()` still exists for compatibility but is not used by the package.
Test: `test_value_filters_do_not_leak_between_views`.

## BUG-3 Unknown ordering field returns 500

With `ordering_fields = "__all__"` (or none), `?ordering=doesnotexist` raises `FieldError` → 500.
Verified on `/book/aggregation/?aggregation=count&group_by=author&ordering=doesnotexist`.

**Fixed:** unknown terms are not result columns and are dropped (SEC-2), like DRF's `OrderingFilter` does.
Test: `test_unknown_ordering_field_is_ignored`.

## BUG-4 `count` assumes a primary key named `id`

`get_annotation()` uses `models.Count("id")` (`aggregator.py:31`). Models with a different primary key
name (e.g. `uuid = UUIDField(primary_key=True)`) raise `FieldError`.

**Fixed:** `models.Count("pk")`. Test: `test_count_with_primary_key_not_named_id` (`Publisher` has a
`CharField` primary key).

## BUG-5 Numeric type check is too narrow

`validate_params()` compares `get_internal_type()` against a fixed list (`aggregator.py:111-125`).
Rejected even though they work: `BigIntegerField`, `SmallIntegerField`, `PositiveIntegerField`,
`PositiveSmallIntegerField`, `PositiveBigIntegerField`, `AutoField`, `BigAutoField`, `DurationField`
(sum/avg), and `TimeField` (min/max).

**Partly fixed:** all integer types (`BigIntegerField`, `SmallIntegerField`, the `Positive*` and `*AutoField`
variants) are accepted (`NUMBER_FIELD_TYPES` in `aggregator.py`). Test: `test_integer_field_variants`.
Still open: `DurationField` for sum/avg and `TimeField` for min/max, which need their own tests.

## BUG-6 Value filters are always `NumberFilter`

`convert_to_filter_fields()` only creates `NumberFilter`s (`filter.py:15,19`).
Verified: `max` on `pubdate` with `value__gt=2020-01-01` gives `400 {"value__gt": ["Enter a number."]}`.

**Fix:** choose the filter class from the aggregated field's type.

## BUG-7 Count on an empty queryset returns an empty list

Without `group_by`, `count` on zero rows returns `[]` because there is no row to group.
Verified with `?aggregation=count&name__icontains=zzz`. Clients would expect `[{"group": "all", "value": 0}]`.

**Fix:** for the ungrouped case use `queryset.aggregate()` and wrap the result in one row.

## BUG-8 `group_by` whitespace is not stripped

`group_by=author, name` → `400 'group_by' is not valid` (verified), while `ordering` strips spaces.

**Fixed:** each part is stripped, both in `get_filtered_params()` and in `AggregationSerializer`, which parses
`group_by` again (BUG-13). Empty parts (`author,`) are still rejected with 400. Test: `test_group_by_with_whitespace`.

## BUG-9 The magic `group` annotation

Without `group_by` the queryset gets
`annotate(group=Case(When(pk__isnull=False, then=Value("all")), default=Value("test")))`
(`aggregator.py`). `"test"` is leftover. The `Case` looks unnecessary but is not: it references `pk`, which keeps a
`GROUP BY` in the query. With a plain `Value("all")` Django drops the `GROUP BY` (verified), so an empty
queryset returns one row with `0` instead of `[]` (BUG-7) and value filters become a `HAVING` without
`GROUP BY`. Replacing it is a behaviour change and belongs with BUG-7.
On a model with a field named `group`, the annotation collides (`ValueError` → 500), and
`group_by=group` is checked against the model and rejected.

**Fix:** `Value("all")` under a name that cannot collide, or the `aggregate()` path from BUG-7.

## BUG-10 String `ordering_fields` match substrings

`term in ordering_fields` (`mixins.py:71`) does substring matching when `ordering_fields` is a string
other than `"__all__"`, e.g. `"name"` allows `na`.

**Fixed:** a string other than `"__all__"` is normalized to a one-element list.
Test: `test_string_ordering_fields_match_whole_names`.

## BUG-11 Translated aggregation names

The enum values contain `gettext_lazy` versions (`enums.py:7-11`), so accepted API values depend on the
active language. An API parameter should not change with the locale, and the error message lists names twice.

**Fix:** plain strings for parameter values; translate only messages.

## BUG-12 Annotation type lookup can raise

`get_field_type()` reads `annotation.output_field` (`aggregator.py:67`). For expressions with mixed
types and no explicit `output_field`, Django raises `FieldError` → 500 instead of a 400.

**Fixed:** `get_field_type()` catches `FieldError` and returns no type, so the request is rejected with
`400 'aggregation_field' must be a number field`. Test: `test_aggregation_field_with_unresolvable_type`.

## BUG-13 Serializer re-parses `group_by`

`AggregationSerializer.__init__` reads `group_by` from the request again (`serializers.py:28-34`),
separately from `get_filtered_params()`. Both have to stay in sync. Also:
`get_aggregation_serializer_class()` returns an instance, not a class; `PassTroughField` is a typo
(`PassThroughField`); the docstring names a person.

**Fix:** pass the validated `group_by` in the serializer context; rename with deprecation aliases.

## BUG-14 Two tests fail on exact float comparison

`test_sum` and `test_avg` compare `76.96000000000001` with `76.96` (verified on Django 4.2.30, 5.2 and 6.1.2,
SQLite 3.46).

**Fixed:** the two float comparisons in `test_sum` and `test_avg` use `assertAlmostEqual`.

---

## PKG-1 Runtime dependencies are not declared

**Fixed:** `pyproject.toml` declares `Django>=4.2`, `djangorestframework>=3.14` and `django-filter>=23.5`
(lower bounds, no `~=` pins in a library). The `requirements*.txt` files were replaced by uv dependency
groups and a committed `uv.lock`.

## PKG-2 Supported versions are out of date

**Fixed:** `requires-python = ">=3.10"`, `Django>=5.2`, `djangorestframework>=3.16`, `django-filter>=25.1`
(the first DRF and django-filter releases that support Django 5.2), plus Python and Django classifiers.
Verified locally with the lowest versions on Python 3.10, Django 5.2.18 and the latest versions on Python 3.14
(only BUG-14 fails). The test matrix is in CI since PKG-4.

## PKG-3 Tests import from `src.`

`tests/views.py` (now `tests/testapp/views.py`) imported `src.django_rest_aggregation.mixins`, so tests ran
against the source tree instead of the installed package and only worked from the repo root.

**Fixed:** `uv sync` installs the package in editable mode and the tests import `django_rest_aggregation`.

## PKG-4 No CI for tests

`ci.yml` runs ruff on pushes to `main` and on pull requests, but no tests. `publish.yml` is triggered on
`release: created` and does not wait for CI.

**Fixed:** `ci.yml` has test jobs (Python × Django matrix on SQLite,
PostgreSQL and SQL Server services) and runs on every push. `publish.yml` triggers on `release: published`,
calls `ci.yml` as a reusable workflow and uploads only after it passes. Not yet run on GitHub at the time of
writing.

## PKG-5 Packaging metadata and tooling

- `pyproject.toml`: leftover `#Todo`, no `license`, no `__version__`.
- `__init__.py` is empty; users import from `django_rest_aggregation.mixins`.
- `runtests.py` contains commented-out coverage code; the SQLite DB is written to the repo root.

**Fixed:** `pyproject.toml` declares `license = "MIT"` and `license-files` (PEP 639, setuptools ≥ 77; the
license classifier was dropped, as PEP 639 requires) and the `#Todo` is gone. `django_rest_aggregation.__version__`
reads the installed version, so `pyproject.toml` stays the only place to bump it. `AggregationMixin` can be
imported from the package root (lazily, so importing the package does not need Django settings);
`django_rest_aggregation.mixins` keeps working. Coverage is configured in `pyproject.toml` and tests use an
in-memory SQLite DB.

## PKG-6 README links on PyPI

`pyproject.toml` uses `README.md` as the PyPI description. The signpost README links to `Readme/*.md`
with relative paths, which do not resolve on PyPI.

**Fix:** absolute GitHub URLs in `README.md`, or set the PyPI `[project.urls]` "Documentation" entry and
keep the README's install and quickstart text self-contained.

---

## Optimizations and ideas

- Several aggregations per request (`aggregation=sum,avg`) in one query.
- `count_distinct` / `distinct=True` option, since joins can count rows twice.
- Standard DRF error shape (`{"aggregation": ["…"]}`) instead of `{"error": "…"}`.
- ~~Type hints and a `py.typed` marker.~~ Done: `src/` is fully typed, checked with ty, and ships `py.typed`.
- Replace `HelperView` by calling the FilterSet directly:
  `filterset_class(request.query_params, queryset=qs, request=request).qs`.
- Document that the action inherits the view's permissions and `get_queryset()` scoping.
- An OpenAPI schema for the action (drf-spectacular `extend_schema`).
- Short `CHANGELOG.md`; commit messages are the only history at the moment.

Related: [Architecture](architecture.md) · [Development](development.md)
