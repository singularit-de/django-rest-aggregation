# View attributes

Class attributes `AggregationMixin` reads from the view:

| Attribute | Default | Meaning | Note |
|-----------|---------|---------|------|
| `aggregation_name` | `"value"` | Key of the aggregated value | [Customization](customization.md) |
| `aggregation_serializer_class` | `AggregationSerializer` | Serializer for result rows | [Customization](customization.md) |
| `aggregated_filterset_class` | built from `aggregated_filterset_fields` | FilterSet applied after aggregation | [Filtering](filtering.md) |
| `aggregated_filterset_fields` | – | Shortcut: lookups for value filters, or `"__all__"` | [Filtering](filtering.md) |
| `aggregated_ordering_fields` | falls back to `ordering_fields` | Further restricts `ordering` terms | [Ordering](ordering.md) |
| `aggregation_fields` | readable fields of the view's serializer | Fields allowed in `group_by` and `aggregation_field`, or `"__all__"` | [Field access](field-access.md) |
| `aggregation_models` | – | Related models whose fields are allowed in addition, as classes or `"app_label.ModelName"` | [Field access](field-access.md) |
| `aggregation_max_group_by` | `3` | Maximum number of `group_by` fields, `None` for no limit | [Field access](field-access.md) |

Earlier versions of the README called two of these `aggregated_filtering_class` and
`aggregated_filtering_fields`. Those names do nothing; the code reads `aggregated_filterset_class`
and `aggregated_filterset_fields`.

Standard DRF attributes are respected as well: `get_queryset()`, `filter_backends`,
`filterset_class`, `ordering_fields`, `permission_classes`, `pagination_class`.
