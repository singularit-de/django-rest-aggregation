# Ordering

Order results with the `ordering` parameter, comma-separated, `-` for descending:

```
/book/aggregation/?aggregation=count&group_by=author&ordering=-value,author
```

Which fields are allowed is decided in this order:

1. `aggregated_ordering_fields` on the view, if set
2. otherwise `ordering_fields` (the attribute DRF's `OrderingFilter` uses)
3. if neither is set, or the list contains `"__all__"`, or the value is the string `"__all__"`,
   **any** ordering is applied

Disallowed terms are dropped silently.

```python
class BookViewSet(AggregationMixin, GenericViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    aggregated_ordering_fields = ["value", "author"]
```

**Only order by `value` (or your `aggregation_name`) and fields that are in `group_by`.**
Ordering by any other field adds that field to the SQL `GROUP BY` and returns wrong,
ungrouped results ([BUG-1](issues.md#bug-1-ordering-by-a-non-grouped-field-breaks-the-aggregation)).
With the permissive default (step 3), an unknown field name returns `500`
([BUG-3](issues.md#bug-3-unknown-ordering-field-returns-500)).

The `ordering` parameter is also read by `OrderingFilter`, which runs before aggregation.

Related: [Filtering](filtering.md) · [Grouping](grouping.md)
