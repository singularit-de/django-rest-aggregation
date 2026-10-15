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

## Allowing related models

Instead of listing every path, release whole related models with `aggregation_models` (classes or
`"app_label.ModelName"`). It adds to the allowed fields above, so either attribute alone is enough:

```python
class BookViewSet(AggregationMixin, GenericViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer  # Book fields: what the serializer shows
    aggregation_models = [Author, "shop.Store"]
```

A relation path is allowed if **every model it passes through after the view's model** is listed:

| Path | Models after `Book` | Allowed |
|------|---------------------|---------|
| `author__name`, `author__age` | `Author` | yes |
| `stores__name` | `Store` | yes |
| `author__agent__name` | `Author`, `Agent` | no, `Agent` is not listed |
| `stores__books__price` | `Store`, `Book` | no, `Book` is not listed |

The view's model gets no exception: a path that leads back to it would otherwise bypass its field allowlist.
List it in `aggregation_models` only if all its fields may be used. Fields of the view's model itself and
annotations are never allowed through `aggregation_models`, only through `aggregation_fields` (or the
serializer). A listed model is released with all its fields, through any path.

Override `get_aggregation_models()` to decide per request.

## Limits

- At most `aggregation_max_group_by` group fields (default `3`, `None` for no limit); more give
  `400 'group_by' accepts at most 3 fields`.
- Relation depth is limited by the allowlist: only the paths listed (or exposed by the serializer) and paths
  through models in `aggregation_models` work.
- Results are not limited in size; use a `pagination_class` for endpoints with many groups.

## Ordering

`ordering` is limited to the result columns, see [Ordering](ordering.md).

Related: [View attributes](view-attributes.md) · [Grouping](grouping.md) · [Aggregations](aggregations.md)
