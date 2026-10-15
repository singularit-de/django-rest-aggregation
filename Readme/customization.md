# Customization

## Name of the aggregated value

`aggregation_name` renames the `value` key in the response. Filters and ordering use the new name.

```python
class BookViewSet(AggregationMixin, GenericViewSet):
    aggregation_name = "total"
    aggregated_filterset_fields = ["gt"]
```

```
/book/aggregation/?aggregation=count&group_by=author&total__gt=5&ordering=-total
```

## Serializer

The default `AggregationSerializer` outputs the aggregated value plus the `group_by` fields
(or `group` when ungrouped), passing values through unchanged.

`aggregation_serializer_class` replaces it. The serializer is built with
`many=True` and the context keys `request` and `name` (the aggregation name).
Each item is a `dict`, because the queryset is a `.values()` queryset.

```python
class RoundedAggregationSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {key: round(val, 1) if isinstance(val, float) else val for key, val in instance.items()}


class BookViewSet(AggregationMixin, GenericViewSet):
    aggregation_serializer_class = RoundedAggregationSerializer
```

## Pagination

The action uses the view's `pagination_class`. Paginated responses have the usual
`count` / `next` / `previous` / `results` shape. Add an `ordering`, otherwise Django
warns about unordered pagination and pages may be inconsistent.

## Overriding hooks

These methods on `AggregationMixin` can be overridden:

| Method | Purpose |
|--------|---------|
| `get_aggregation_name()` | Name of the value key |
| `get_aggregation_serializer_class(*args, **kwargs)` | Returns a serializer **instance** (despite the name) |
| `filter_aggregated_queryset(queryset)` | Filtering after aggregation |
| `order_aggregated_queryset(queryset)` | Ordering after aggregation |
| `get_aggregation_fields()` | Fields allowed in `group_by` / `aggregation_field` ([Field access](field-access.md)) |
| `get_aggregation_max_group_by()` | Maximum number of `group_by` fields |

Related: [View attributes](view-attributes.md) · [Architecture](architecture.md)
