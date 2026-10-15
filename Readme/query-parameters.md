# Query parameters

| Parameter | Required | Meaning | Example |
|-----------|----------|---------|---------|
| `aggregation` | yes | Aggregation type, see [Aggregations](aggregations.md) | `aggregation=sum` |
| `aggregation_field` | for everything except `count` | Field to aggregate | `aggregation_field=price` |
| `group_by` | no | Comma-separated grouping fields, see [Grouping](grouping.md) | `group_by=author,pubdate` |
| `value__gt`, `value__lte`, … | no | Filter on the aggregated value, see [Filtering](filtering.md) | `value__gt=1000` |
| `ordering` | no | Comma-separated result ordering, see [Ordering](ordering.md) | `ordering=-value` |

`aggregation`, `aggregation_field` and `group_by` may each appear only once.
Repeating one returns `400`; for `group_by` use commas instead.

`value` is the default name of the aggregated field. If the view sets `aggregation_name`, use that name
in filters and ordering instead (see [Customization](customization.md)).

Any other parameter goes to the view's normal filter backends and filters rows **before** aggregation.

Validation errors come back as `400` with the shape `{"error": "<message>"}`.
