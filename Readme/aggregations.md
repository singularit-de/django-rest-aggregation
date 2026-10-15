# Aggregations

| `aggregation=` | Aliases | Needs `aggregation_field` | Allowed field types |
|----------------|---------|---------------------------|---------------------|
| `count` | – | no | – (counts rows) |
| `sum` | – | yes | integer fields (`IntegerField`, `BigIntegerField`, `PositiveIntegerField`, …), `FloatField`, `DecimalField` |
| `average` | `avg` | yes | integer fields, `FloatField`, `DecimalField` |
| `minimum` | `min` | yes | numeric types above, `DateField`, `DateTimeField` |
| `maximum` | `max` | yes | numeric types above, `DateField`, `DateTimeField` |

The type check uses the field's `get_internal_type()`. All built-in integer fields are accepted (including the
`Positive*` and `*AutoField` variants); `DurationField` and `TimeField` are currently rejected
([BUG-5](issues.md#bug-5-durationfield-and-timefield-are-rejected)).

`aggregation_field` can be any of the following, as far as the view allows it ([Field access](field-access.md)):

- a model field: `aggregation_field=price`
- a field on a related model, using `__`: `aggregation_field=author__age`
- an annotation added in the view's `get_queryset()`: `aggregation_field=price_per_page`

The aggregation is built in `get_annotation()` in `src/django_rest_aggregation/aggregator.py`,
and the aliases live in the `Aggregation` enum in `enums.py`.

Related: [Grouping](grouping.md) · [Query parameters](query-parameters.md)
