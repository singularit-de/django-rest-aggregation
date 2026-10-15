# Architecture

Package: `src/django_rest_aggregation/` (about 300 lines).

| Module | Contents |
|--------|----------|
| `mixins.py` | `AggregationMixin` (the `aggregation` action, post-filtering, ordering), `HelperView` |
| `aggregator.py` | `Aggregator` (validation + `.values().annotate()`), parameter parsing, field lookup helpers |
| `enums.py` | `Aggregation` enum with names and aliases |
| `filter.py` | `ValueFilter` and `convert_to_filter_fields()` for value filters |
| `serializers.py` | `AggregationSerializer`, `PassTroughField` |

## Request flow (`AggregationMixin.aggregation`)

1. `self.filter_queryset(self.get_queryset())`: the view's normal filter backends
   (including `OrderingFilter`) run on the model queryset.
2. `Aggregator(request, queryset, name)`: `get_filtered_params()` reads `aggregation`,
   `aggregation_field` and `group_by` from the query string.
3. `Aggregator.get_aggregated_queryset()`:
   - `validate_params()` checks the aggregation, field existence and field type
   - without `group_by`, annotates a constant `group` column
   - returns `queryset.values(*group_by).annotate(<name>=<Aggregate>)`
4. `filter_aggregated_queryset()`: runs `DjangoFilterBackend` with the value FilterSet,
   using `HelperView` as a fake view that only carries `filterset_class`.
5. `order_aggregated_queryset()`: applies `ordering` after the allowlist check.
6. Pagination and serialization as in a normal list action.

The whole result is a single SQL `SELECT … GROUP BY …` with an optional `HAVING`
from the value filters.

## Field resolution

`model_field_exists()` / `get_field_type()` walk `__`-separated paths with
`_meta.get_field()` and `related_model`. Annotations are looked up in
`queryset.query.annotations`, but only by their exact name (no `annotation__x` paths).

Related: [Development](development.md) · [Issues](issues.md)
