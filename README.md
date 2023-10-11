# Django Rest Framework Aggregation

---

A simple Django Rest Framework extension to add aggregation endpoints to your API.

Key features:

- count, sum, average, minimum, maximum, percentile &#10060; and percent&#10060;
- grouping by multiple fields &#10060;
- limiting the number of results &#10060;

---

## Installation

For installing use pip: &#10060;

    pip install [COMING SOON] 

## Usage

Create a ViewSet using the **AggregationViewSet** class or use the **AggregationMixin** in your own ViewSet.

```python
from django_rest_aggregation.mixins import AggregationMixin
from django_rest_aggregation.viewsets import AggregationViewSet

...


class AuthorViewSet(GenericViewSet, AggregationMixin):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class BookViewSet(AggregationViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
```

Register the ViewSet in your urls.py. The default aggregation endpoint is **{base_url}/aggregation/**.

```python
router = DefaultRouter()
router.register(r'author', AuthorViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('book/custom/endpoint/', BookViewSet.as_view({'get': 'aggregation'})
]
```

Get the aggregation results by sending a GET request to the aggregation endpoint.

| URL                                                                                            | What it does                             |
|------------------------------------------------------------------------------------------------|------------------------------------------|
| ```/book/aggregation/?aggregation=count ```                                                    | Get the number of books                  |
| ```/book/aggregation/?aggregation=maximum&aggregationField=price```                            | Get the most expensive book              |
| ```/book/aggregation/?aggregation=average&aggregationField=rating&aggregationGroupBy=author``` | Get the average rating grouped by author |
| &#10060;                                                                                       | &#10060;                                 |

## Query parameter overview
| query parameter    | description                        | example                         |
|--------------------|------------------------------------|---------------------------------|
| aggregation        | determines the type of aggregation | ```aggregation=sum```           |
| aggregationField   | the field to aggregate on          | ```aggregationField=price```    |
| aggregationGroupBy |                                    | ```aggregationGroupBy=author``` |



## Aggregations
Available aggregations are:
 - count
 - sum
 - average
 - minimum
 - maximum
 - percentile &#10060;
 - percent &#10060;

They can be used by adding the mandatory **aggregation** parameter to the request URL. 

        /book/aggregation/?aggregation=count


### Aggregation Field
The aggregation field is the field to aggregate on. 
It can be used by adding the **aggregationField** parameter to the request URL. 
This is a mandatory parameter for the **sum**, **average**, **minimum** and **maximum** aggregations.

        /book/aggregation/?aggregation=sum&aggregationField=price

You gan also use the double underscore notation to aggregate on a related field.

        /book/aggregation/?aggregation=sum&aggregationField=author__age

## Grouping
Grouping is done by adding the **aggregationGroupBy** parameter to the request URL. 

        /book/aggregation/?aggregation=count&aggregationGroupBy=author

You can group throughout multiple relations (ForeignKey & ManyToMany Fields) by using the double underscore notation.

        /store/aggregation/?aggregation=count&aggregationGroupBy=books__author__age

To group by multiple fields, separate them with a comma. &#10060;

        /book/aggregation/?aggregation=count&aggregationGroupBy=author,genre &

## Sorting &#10060;
## Limiting &#10060;