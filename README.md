You can find the original Project here: https://github.com/kit-oz/drf-aggregation

# Django Rest Framework Aggregation

---

A simple Django Rest Framework extension to add aggregation endpoints to your API.

Key features:

- count, sum, average, minimum, maximum
- grouping by multiple fields
- filtering and ordering

---

## Installation

To install, use pip

    pip install django-rest-aggregation

## Quickstart

Inherit the **AggregationMixin** in your ViewSet.

```python
from django_rest_aggregation.mixins import AggregationMixin

...

class BookViewSet(GenericViewSet, AggregationMixin):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
```

Register the ViewSet in your `urls.py`. The default aggregation endpoint is **{base_url}/aggregation/**.

```python
router = DefaultRouter()
router.register(r'book', BookViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # or
    path('book/custom/endpoint/', BookViewSet.as_view({'get': 'aggregation'}))
]
```

Get the aggregation results by sending a GET request to the aggregation endpoint.

| URL                                                                                             | What it does                                                            |
|-------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| ```/book/aggregation/?aggregation=count ```                                                     | Get the total number of books                                           |
| ```/book/aggregation/?aggregation=maximum&aggregation_field=price```                            | Get the most expensive book                                             |
| ```/book/aggregation/?aggregation=average&aggregation_field=rating&group_by=author```           | Get the average rating grouped by author                                |
| ```/book/aggregation/?aggregation=sum&aggregation_field=pages&group_by=author&value__gt=1000``` | Get the sum of all pages grouped by authors which are greater than 1000 |

## Parameter overview

### URL Parameters

| query parameter   | description                                | example                       |
|-------------------|--------------------------------------------|-------------------------------|
| aggregation       | determines the type of aggregation         | ```aggregation=sum```         |
| aggregation_field | the field to aggregate on                  | ```aggregation_field=price``` |
| group_by          | the field on which the queryset is grouped | ```group_by=author```         |
| value             | the value to filter the queryset           | ```value__gt=1000```          |

### View Class Variables

| class variable               | description                                          | example                                             |
|------------------------------|------------------------------------------------------|-----------------------------------------------------|
| aggregation_name             | changes the default value name                       | ```aggregation_name=foo```                          |
| aggregation_serializer_class | Sets a custom serializer for the queryset            | ```aggregation_serializer_class=CustomSerializer``` |
| aggregated_filtering_class   | Sets a FilterSet Class for filtering the value field | ```aggregated_filtering_class=ValueFilter```        |
| aggregated_filterset_fields  | A shortcut for setting a value Filtersets            | ```aggregated_filterset_fields=[lt, lte, gt]```     |

## Aggregations

Available aggregations are:

- count
- sum
- average
- minimum
- maximum

They can be used by adding the mandatory **aggregation** parameter to the request URL.

        /book/aggregation/?aggregation=count

### Aggregation Field

The aggregation field is the field to aggregate on.
It can be used by adding the **aggregation_field** parameter to the request URL.
This is a mandatory parameter for the **sum**, **average**, **minimum** and **maximum** aggregations.
Both model fields and annotated fields can be used.

        /book/aggregation/?aggregation=sum&aggregation_field=price

You can also use the double underscore notation to aggregate on related model fields.

        /book/aggregation/?aggregation=sum&aggregation_field=author__age

If the aggregation is sum or average, the aggregation field must be a numeric field. If the aggregation is min or
max, the aggregation field must be date or numeric field.

## Grouping

Grouping is done by adding the **group_by** parameter to the request URL.
Again, model fields and annotated fields can be used.

        /book/aggregation/?aggregation=count&group_by=author

You can group throughout multiple model relations (ForeignKey & ManyToMany Fields) by using the double underscore
notation.

        /store/aggregation/?aggregation=count&group_by=books__author__age

To group by multiple fields, separate them with a comma.

        /book/aggregation/?aggregation=count&group_by=author,genre

## Filtering & Ordering
To filter the queryset, you can use the standard Django Filter Backend.
That implies:
 - filtering before aggregation

        /book/aggregation/?aggregation=count&group_by=author&pages__gt=100

 -  filtering after aggregation

        /book/aggregation/?aggregation=count&group_by=author&value__gt=5
 - combined filtering

        /book/aggregation/?aggregation=count&group_by=author&pages__gt=100&value__gt=100

To control which filtering options are available, you can use the **aggregated_filtering_class** class variable.
This sets a custom FilterSet Class for filtering the value field.

```python
class BookViewSet(GenericViewSet, AggregationMixin):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    aggregated_filtering_class = ValueFilter

class ValueFilter(filters.FilterSet):
    value__gte = filters.NumberFilter(field_name='test123', lookup_expr='gte')
    value__lte = filters.NumberFilter(field_name='test123', lookup_expr='lte')

    class Meta:
        fields = ['test123__gte', 'test123__lte']
```
A shortcut for setting value Filtersets is the **aggregated_filtering_fields** class variable.
This automatically creates a FilterSet class for filtering the value field.

```python
class BookViewSet(GenericViewSet, AggregationMixin):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    aggregated_filtering_fields = ['lt', 'lte', 'gt']
```
You can use 'lt', 'lte', 'gt', 'gte', 'exact' and  &#95;&#95;all&#95;&#95; as values for the **aggregated_filtering_fields** class variable.

Fields available for ordering the result are taken from the `aggregated_ordering_fields` attribute.
```python
class BookViewSet(GenericViewSet, AggregationMixin):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    aggregated_ordering_fields = ['value', 'grouped_by_field']
```
if this is not set available fields are taken from the usual `ordering_fields` attribute.
The reason for this behaviour is to accommodate interplay with the often used `OrderingFilter` 
```python
class BookViewSet(GenericViewSet, AggregationMixin):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    ordering_fields = ['page_count', 'author']
```
If no ordering fields of any kind are specified or the list contains `"__all__"` any passed ordering will be tried to be applied.
``ordering_fields = __all__`` is also possible.

