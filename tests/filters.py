from django_filters import rest_framework as filters

from .models import Book, Author


class BookFilter(filters.FilterSet):
    class Meta:
        model = Book
        fields = {
            'name': ['icontains'],
            'pages': ['gte', 'lte', 'gt', 'lt'],
            'price': ['gte', 'lte', 'gt', 'lt'],
            'rating': ['gte', 'lte', 'gt', 'lt'],
            'authors__name': ['icontains'],
            'publisher__name': ['icontains'],
            'pubdate': ['gte', 'lte', 'gt', 'lt'],
        }


class AuthorFilter(filters.FilterSet):
    class Meta:
        model = Author
        fields = {
            'name': ['icontains'],
            'age': ['gte', 'lte', 'gt', 'lt'],
        }


class ValueFilter(filters.FilterSet):
    value__gte = filters.NumberFilter(field_name='value', lookup_expr='gte')
    value__lte = filters.NumberFilter(field_name='value', lookup_expr='lte')
    value__gt = filters.NumberFilter(field_name='value', lookup_expr='gt')
    value__lt = filters.NumberFilter(field_name='value', lookup_expr='lt')

    class Meta:
        fields = ['value__gte', 'value__lte', 'value__gt', 'value__lt']
