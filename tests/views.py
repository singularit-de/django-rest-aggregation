from django.db.models import F, Case, When, Value, BooleanField
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter

from django_rest_aggregation.mixins import AggregationMixin
from django_rest_aggregation.viewsets import AggregationViewSet
from .filters import BookFilter
from .models import Author, Book, Publisher, Store
from .serializer import AuthorSerializer, BookSerializer, PublisherSerializer, StoreSerializer


class AuthorViewSet(AggregationViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = "__all__"
    search_fields = ["name"]


class BookViewSet(viewsets.ModelViewSet, AggregationMixin):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]

    filterset_class = BookFilter
    ordering_fields = "__all__"
    search_fields = ["name", "authors__name", "publisher__name"]

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
