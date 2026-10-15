# Filtering

Filtering happens in two places.

**Before aggregation:** the view's own `filter_backends` (e.g. `DjangoFilterBackend` with a `filterset_class`)
filter the rows that get aggregated.

```
/book/aggregation/?aggregation=count&group_by=author&pages__gt=100
```

**After aggregation:** a second FilterSet filters on the aggregated value.

```
/book/aggregation/?aggregation=count&group_by=author&value__gt=5
```

Both can be combined:

```
/book/aggregation/?aggregation=count&group_by=author&pages__gt=100&value__gt=5
```

## Setting up value filters

Shortcut: list the lookups in `aggregated_filterset_fields`.
Allowed entries are `"lt"`, `"lte"`, `"gt"`, `"gte"`, `"exact"`, or the string `"__all__"` for all of them.

```python
class BookViewSet(AggregationMixin, GenericViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    aggregated_filterset_fields = ["lt", "lte", "gt"]
```

This creates `value__lt`, `value__lte`, `value__gt` (and `value` for `exact`).

Full control: set your own FilterSet in `aggregated_filterset_class`. Its `field_name`
must be the aggregation name (`value` unless [`aggregation_name`](customization.md) is set):

```python
from django_filters import rest_framework as filters


class ValueFilter(filters.FilterSet):
    value__gte = filters.NumberFilter(field_name="value", lookup_expr="gte")
    value__lte = filters.NumberFilter(field_name="value", lookup_expr="lte")


class BookViewSet(AggregationMixin, GenericViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    aggregated_filterset_class = ValueFilter
```

Known limits:

- Value filters are always `NumberFilter`, so `max`/`min` on a date field cannot be filtered
  by date ([BUG-6](issues.md#bug-6-value-filters-are-always-numberfilter)).

Related: [View attributes](view-attributes.md) · [Ordering](ordering.md)
