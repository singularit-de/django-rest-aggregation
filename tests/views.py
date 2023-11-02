from django.db.models import F, Case, When, Value, BooleanField
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter

from django_rest_aggregation.mixins import AggregationMixin
from .filters import BookFilter, Test123Filter, AuthorFilter
from .models import Book, Store, Author
from .serializer import BookSerializer, StoreSerializer, AuthorSerializer


class BookViewSet(viewsets.ModelViewSet, AggregationMixin):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]

    filterset_class = BookFilter
    ordering_fields = "__all__"
    aggregated_filtering_fields = ["gte", "lte", "gt", "lt", "exact"]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.annotate(price_per_page=F('price') / F('pages'),
                                 expensive=Case(
                                     When(price__gt=17, then=Value(True)),
                                     default=Value(False),
                                     output_field=BooleanField()))


class StoreViewSet(viewsets.ModelViewSet, AggregationMixin):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer


class AuthorViewSet(viewsets.ModelViewSet, AggregationMixin):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]

    filterset_class = AuthorFilter
    aggregated_filterset_class = Test123Filter
    aggregation_name = "test123"
    ordering_fields = "__all__"
