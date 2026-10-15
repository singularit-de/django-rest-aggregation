# Issues: open bugs and ideas

Open issues only. Fixed entries are removed; IDs are kept stable and not reused, so gaps in the numbering
are fixed issues. Re-evaluated against the current code on 2026-10-15.

**Verified** = reproduced against the test app with a probe script.
**From code** = read from the source, not run.

## Overview

| ID | Severity | Topic | Status |
|----|----------|-------|--------|
| [BUG-5](#bug-5-durationfield-and-timefield-are-rejected) | low | `DurationField` / `TimeField` rejected | verified |
| [BUG-6](#bug-6-value-filters-are-always-numberfilter) | low | Value filters only numeric | verified |
| [BUG-7](#bug-7-count-on-an-empty-queryset-returns-an-empty-list) | low | Empty queryset → `[]` | verified |
| [BUG-9](#bug-9-the-magic-group-annotation) | low | Magic `group` annotation | verified / from code |
| [BUG-11](#bug-11-translated-aggregation-names) | low | Translated aggregation names | from code |
| [BUG-13](#bug-13-serializer-re-parses-group_by) | low | Serializer re-parses `group_by`, naming | from code |
| [OPT](#optimizations-and-ideas) | – | Optimizations and ideas | – |

---

## BUG-5 `DurationField` and `TimeField` are rejected

`validate_params()` accepts the types in `NUMBER_FIELD_TYPES` (all integer types, `FloatField`, `DecimalField`)
and, for min/max, `DATE_FIELD_TYPES` (`DateField`, `DateTimeField`). `DurationField` (sum/avg) and `TimeField`
(min/max) are rejected although Django can aggregate them.

Verified: `sum` on a `DurationField` annotation gives `400 'aggregation_field' must be a number field`.

**Fix:** add `DurationField` to the sum/avg types and `DurationField` / `TimeField` to the min/max types,
with a test per database (duration arithmetic differs between backends).

## BUG-6 Value filters are always `NumberFilter`

`convert_to_filter_fields()` only creates `NumberFilter`s.
Verified: `max` on `pubdate` with `value__gt=2019-01-01` gives `400 {"value__gt": ["Enter a number."]}`.

**Fix:** choose the filter class from the aggregated field's type.

## BUG-7 Count on an empty queryset returns an empty list

Without `group_by`, `count` on zero rows returns `[]` because there is no row to group.
Verified with `?aggregation=count&name__icontains=zzz`. Clients would expect `[{"group": "all", "value": 0}]`.

**Fix:** for the ungrouped case use `queryset.aggregate()` and wrap the result in one row. This changes the
response for empty results, so treat it as a behaviour change.

## BUG-9 The magic `group` annotation

Without `group_by` the queryset gets
`annotate(group=Case(When(pk__isnull=False, then=Value("all")), default=Value("test")))` in
`Aggregator.get_aggregated_queryset()`. `"test"` is leftover. The `Case` looks unnecessary but is not: it
references `pk`, which keeps a `GROUP BY` in the query. With a plain `Value("all")` Django drops the `GROUP BY`
(verified), so an empty queryset returns one row with `0` instead of `[]` (BUG-7) and value filters become a
`HAVING` without `GROUP BY`.

Name collisions:
- An annotation called `group` in the view's `get_queryset()` is silently overwritten (verified: the response
  shows `"group": "all"`).
- A model *field* called `group` makes `annotate()` raise `ValueError` → 500 (from code).

**Fix:** together with BUG-7: use the `aggregate()` path for the ungrouped case, under a key that cannot
collide.

## BUG-11 Translated aggregation names

The enum values in `enums.py` contain `gettext_lazy` versions next to the plain names, so the accepted values
for `aggregation` depend on the active language. Without a translation the lazy strings equal the plain ones
and nothing changes; a project whose locale files translate `count`, `sum`, `average`, … would accept those
translated words as well. An API parameter should not change with the locale. It also makes the type of the
accepted values `str | Promise` instead of `str`.

**Fix:** plain strings for parameter values; translate only messages.

## BUG-13 Serializer re-parses `group_by`

`AggregationSerializer.__init__` reads `group_by` from the request again, separately from
`get_filtered_params()`; both strip the names and have to stay in sync. Also:
`get_aggregation_serializer_class()` returns an instance, not a class; `PassTroughField` is a typo
(`PassThroughField`).

**Fix:** pass the validated `group_by` in the serializer context; rename with deprecation aliases
(these names are public API).

---

## Optimizations and ideas

- Several aggregations per request (`aggregation=sum,avg`) in one query.
- `count_distinct` / `distinct=True` option, since joins can count rows twice.
- Standard DRF error shape (`{"aggregation": ["…"]}`) instead of `{"error": "…"}`.
- Replace `HelperView` by calling the FilterSet directly:
  `filterset_class(request.query_params, queryset=qs, request=request).qs`.
- Document that the action inherits the view's permissions and `get_queryset()` scoping.
- An OpenAPI schema for the action (drf-spectacular `extend_schema`).
- Short `CHANGELOG.md`; commit messages are the only history at the moment. Needed before the 0.5 release,
  whose breaking changes are: `group_by` / `aggregation_field` limited to `aggregation_fields` (serializer
  fields by default), at most 3 `group_by` fields, `ordering` limited to result columns, and the removed hooks
  `remove_invalid_ordering_fields()` and `ValueFilter.set_filter_fields()`.

Related: [Architecture](architecture.md) · [Development](development.md)
