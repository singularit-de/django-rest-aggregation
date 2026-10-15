# Aggregations

| `aggregation=` | Aliases | Needs `aggregation_field` | Allowed field types |
|----------------|---------|---------------------------|---------------------|
| `count` | – | no | – (counts rows) |
| `sum` | – | yes | `IntegerField`, `FloatField`, `DecimalField` |
| `average` | `avg` | yes | `IntegerField`, `FloatField`, `DecimalField` |
| `minimum` | `min` | yes | numeric types above, `DateField`, `DateTimeField` |
| `maximum` | `max` | yes | numeric types above, `DateField`, `DateTimeField` |

The type check uses the field's `get_internal_type()` and matches the names exactly.
Subtypes such as `BigIntegerField` or `PositiveIntegerField` are currently rejected
([BUG-5](issues.md#bug-5-numeric-type-check-is-too-narrow)).

`aggregation_field` can be:

- a model field: `aggregation_field=price`
- a field on a related model, using `__`: `aggregation_field=author__age`
- an annotation added in the view's `get_queryset()`: `aggregation_field=price_per_page`

The aggregation is built in `get_annotation()` in `src/django_rest_aggregation/aggregator.py`,
and the aliases live in the `Aggregation` enum in `enums.py`.

Related: [Grouping](grouping.md) · [Query parameters](query-parameters.md)
