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
            'author__name': ['icontains', 'exact'],
            'pubdate': ['gte', 'lte', 'gt', 'lt'],
        }


class AuthorFilter(filters.FilterSet):
    class Meta:
        model = Author
        fields = {
            'name': ['icontains'],
            'age': ['gte', 'lte', 'gt', 'lt'],
        }


class Test123Filter(filters.FilterSet):
    test123__gte = filters.NumberFilter(field_name='test123', lookup_expr='gte')
    test123__lte = filters.NumberFilter(field_name='test123', lookup_expr='lte')

    class Meta:
        fields = ['test123__gte', 'test123__lte']
