# Ordering

Order results with the `ordering` parameter, comma-separated, `-` for descending:

```
/book/aggregation/?aggregation=count&group_by=author&ordering=-value,author
```

Only the columns of the result can be used: the `group_by` fields and `value` (or your `aggregation_name`;
without `group_by` also `group`). Other terms are dropped silently, like DRF's `OrderingFilter` does.
Ordering by any other field would add it to the SQL `GROUP BY` and break the grouping, or let clients infer
values the endpoint does not show.

The view can restrict this further:

1. `aggregated_ordering_fields` on the view, if set
2. otherwise `ordering_fields` (the attribute DRF's `OrderingFilter` uses)
3. if neither is set, or the list contains `"__all__"`, or the value is the string `"__all__"`,
   all result columns are allowed

```python
class BookViewSet(AggregationMixin, GenericViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    aggregated_ordering_fields = ["value", "author"]
```

The `ordering` parameter is also read by `OrderingFilter`, which runs before aggregation. That ordering is
removed before grouping, so it cannot change the result.

Without `ordering` the order of the rows is not defined and differs between databases.

Related: [Filtering](filtering.md) · [Grouping](grouping.md)
