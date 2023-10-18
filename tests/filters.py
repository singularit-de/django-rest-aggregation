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
