# Grouping

`group_by` groups the queryset before aggregating. It accepts model fields, annotations
and paths across relations (ForeignKey, reverse FK, ManyToMany) written with `__`, as far as the view allows
them ([Field access](field-access.md)), and at most three fields by default:

```
/book/aggregation/?aggregation=count&group_by=author
/store/aggregation/?aggregation=count&group_by=books__author__age
```

Separate several fields with commas; spaces around the names are ignored:

```
/book/aggregation/?aggregation=count&group_by=author,pubdate
```

Each group field becomes a key in the response, next to the aggregated value.

Without `group_by`, the whole queryset is one group with the constant key `"group": "all"`.
On an empty queryset the response is `[]`, not a zero count
([BUG-7](issues.md#bug-7-count-on-an-empty-queryset-returns-an-empty-list)).

Grouping across ManyToMany relations joins rows, so `sum`/`average` may count a row once per joined row.

Related: [Aggregations](aggregations.md) · [Ordering](ordering.md)
