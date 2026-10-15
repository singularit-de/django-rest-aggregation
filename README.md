# Django Rest Framework Aggregation

A Django REST Framework mixin that adds an aggregation endpoint (count, sum, average, minimum, maximum)
with grouping, filtering and ordering to your ViewSets.

```bash
uv add django-rest-aggregation
```

```python
class BookViewSet(AggregationMixin, GenericViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
```

```
GET /book/aggregation/?aggregation=average&aggregation_field=rating&group_by=author
```

Based on [kit-oz/drf-aggregation](https://github.com/kit-oz/drf-aggregation).

## Documentation

The documentation is split into small linked notes in [`Readme/`](Readme/).

**Using the package**

- [Installation](Readme/installation.md): install, dependencies, `INSTALLED_APPS`
- [Quickstart](Readme/quickstart.md): add the mixin, register the route, example requests and responses
- [Query parameters](Readme/query-parameters.md): all URL parameters at a glance
- [Aggregations](Readme/aggregations.md): aggregation types, aliases, allowed field types
- [Grouping](Readme/grouping.md): `group_by`, relation paths, multiple fields
- [Filtering](Readme/filtering.md): filtering before and after aggregation, value FilterSets
- [Ordering](Readme/ordering.md): `ordering`, allowed fields, pitfalls
- [Customization](Readme/customization.md): value name, serializer, pagination, overridable hooks
- [View attributes](Readme/view-attributes.md): reference of all class attributes

**Working on the package**

- [Architecture](Readme/architecture.md): modules and request flow
- [Development](Readme/development.md): setup, tests, lint, release
- [Issues](Readme/issues.md): known vulnerabilities, bugs and optimization ideas

## License

MIT, see [LICENSE](LICENSE).
