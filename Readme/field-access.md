# Field access

`group_by` and `aggregation_field` can only use fields the view allows. Disallowed and unknown fields get
the same `400` (`'group_by' is not valid` / `'aggregation_field' is not valid`), so clients cannot probe
which fields exist.

## Default: what the serializer shows

Without configuration the allowed fields are the readable fields of the view's serializer
(`get_serializer()`), using each field's `source` with `.` written as `__`. Aggregation then reveals nothing
the normal list endpoint does not already show. `SerializerMethodField` and other `source="*"` fields are
not included, and neither are `write_only` fields.

For a `BookSerializer` with `fields = "__all__"`, `group_by=author` works, but `group_by=author__name` does not,
because the serializer only shows the author's primary key.

## Explicit allowlist

List the paths, including relation paths, the endpoint may aggregate over:

```python
class BookViewSet(AggregationMixin, GenericViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    aggregation_fields = ["pages", "price", "author", "author__name", "stores__name"]
```

Annotations from `get_queryset()` are allowed the same way, by name. `aggregation_fields = "__all__"`
restores the behaviour of earlier versions (every model field and every relation path); only use it when
the model holds nothing a client should not see.

Override `get_aggregation_fields()` to decide per request, e.g. by permission.

## Limits

- At most `aggregation_max_group_by` group fields (default `3`, `None` for no limit); more give
  `400 'group_by' accepts at most 3 fields`.
- Relation depth is limited by the allowlist: only the paths listed (or exposed by the serializer) work.
- Results are not limited in size; use a `pagination_class` for endpoints with many groups.

## Ordering

`ordering` is limited to the result columns, see [Ordering](ordering.md).

Related: [View attributes](view-attributes.md) · [Grouping](grouping.md) · [Aggregations](aggregations.md)
