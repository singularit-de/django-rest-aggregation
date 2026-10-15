# Quickstart

Add `AggregationMixin` to a ViewSet. It adds a `GET` action named `aggregation`.

```python
from django_rest_aggregation import AggregationMixin
from rest_framework.viewsets import GenericViewSet


class BookViewSet(AggregationMixin, GenericViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
```

Register it with a router. The endpoint is `{base_url}/aggregation/`:

```python
router = DefaultRouter()
router.register(r"book", BookViewSet)

urlpatterns = [
    path("", include(router.urls)),
    # or bind the action to a custom URL:
    path("book/custom/endpoint/", BookViewSet.as_view({"get": "aggregation"})),
]
```

Example requests:

| URL | Result |
|-----|--------|
| `/book/aggregation/?aggregation=count` | Total number of books |
| `/book/aggregation/?aggregation=maximum&aggregation_field=price` | Highest book price |
| `/book/aggregation/?aggregation=average&aggregation_field=rating&group_by=author` | Average rating per author |
| `/book/aggregation/?aggregation=sum&aggregation_field=pages&group_by=author&value__gt=1000` | Page total per author, only totals above 1000 |

Response without grouping:

```json
[{"group": "all", "value": 42}]
```

Response grouped by `author` (the foreign key value, i.e. the author's pk):

```json
[{"author": 1, "value": 12}, {"author": 2, "value": 30}]
```

The action uses the view's `get_queryset()`, `filter_backends`, permissions and pagination,
so it sees the same rows as the list endpoint.

Related: [Query parameters](query-parameters.md) · [View attributes](view-attributes.md)
