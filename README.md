# Django Rest Framework Aggregation

A Django REST Framework mixin that adds an aggregation endpoint (count, sum, average, minimum, maximum)
with grouping, filtering and ordering to your ViewSets.

```bash
uv add django-rest-aggregation
```

```python
from django_rest_aggregation import AggregationMixin
from rest_framework.viewsets import GenericViewSet


class BookViewSet(AggregationMixin, GenericViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
```

```
GET /book/aggregation/?aggregation=average&aggregation_field=rating&group_by=author
```

Based on [kit-oz/drf-aggregation](https://github.com/kit-oz/drf-aggregation).

## Documentation

The documentation is split into small linked notes in [`Readme/`](https://github.com/singularit-de/django-rest-aggregation/tree/main/Readme).

**Using the package**

- [Installation](https://github.com/singularit-de/django-rest-aggregation/blob/main/Readme/installation.md): install, dependencies, `INSTALLED_APPS`
- [Quickstart](https://github.com/singularit-de/django-rest-aggregation/blob/main/Readme/quickstart.md): add the mixin, register the route, example requests and responses
- [Query parameters](https://github.com/singularit-de/django-rest-aggregation/blob/main/Readme/query-parameters.md): all URL parameters at a glance
- [Aggregations](https://github.com/singularit-de/django-rest-aggregation/blob/main/Readme/aggregations.md): aggregation types, aliases, allowed field types
- [Grouping](https://github.com/singularit-de/django-rest-aggregation/blob/main/Readme/grouping.md): `group_by`, relation paths, multiple fields
- [Filtering](https://github.com/singularit-de/django-rest-aggregation/blob/main/Readme/filtering.md): filtering before and after aggregation, value FilterSets
- [Ordering](https://github.com/singularit-de/django-rest-aggregation/blob/main/Readme/ordering.md): `ordering`, allowed fields, pitfalls
- [Field access](https://github.com/singularit-de/django-rest-aggregation/blob/main/Readme/field-access.md): which fields `group_by` / `aggregation_field` may use, limits
- [Customization](https://github.com/singularit-de/django-rest-aggregation/blob/main/Readme/customization.md): value name, serializer, pagination, overridable hooks
- [View attributes](https://github.com/singularit-de/django-rest-aggregation/blob/main/Readme/view-attributes.md): reference of all class attributes

**Working on the package**

- [Architecture](https://github.com/singularit-de/django-rest-aggregation/blob/main/Readme/architecture.md): modules and request flow
- [Development](https://github.com/singularit-de/django-rest-aggregation/blob/main/Readme/development.md): setup, tests, lint, release
- [Issues](https://github.com/singularit-de/django-rest-aggregation/blob/main/Readme/issues.md): open bugs, packaging problems and ideas

## License

MIT, see [LICENSE](https://github.com/singularit-de/django-rest-aggregation/blob/main/LICENSE).
