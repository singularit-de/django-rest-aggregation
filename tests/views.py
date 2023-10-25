from django.db.models import F, Case, When, Value, BooleanField
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter

from django_rest_aggregation.mixins import AggregationMixin
from .filters import BookFilter, ValueFilter
from .models import Book, Publisher, Store
from .serializer import BookSerializer, PublisherSerializer, StoreSerializer


class BookViewSet(viewsets.ModelViewSet, AggregationMixin):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]

    filterset_class = BookFilter
    ordering_fields = "__all__"
    search_fields = ["name", "authors__name", "publisher__name"]

    aggregated_filterset_class = ValueFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.annotate(price_per_page=F('price') / F('pages'),
                                 expensive=Case(
                                     When(price__gt=20, then=Value(True)),
                                     default=Value(False),
                                     output_field=BooleanField()))


class PublisherViewSet(viewsets.ModelViewSet, AggregationMixin):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer


class StoreViewSet(viewsets.ModelViewSet, AggregationMixin):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
