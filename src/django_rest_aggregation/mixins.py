from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Literal

from django.db.models import QuerySet
from django_filters import FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from .aggregator import Aggregator
from .filter import FilterFields, ValueFilter
from .serializers import AggregationSerializer

if TYPE_CHECKING:
    from rest_framework.generics import GenericAPIView

    # The mixin is used with DRF's GenericAPIView / ViewSets and relies on their attributes.
    _MixinBase = GenericAPIView[Any]
else:
    _MixinBase = object


class AggregationMixin(_MixinBase):
    # Optional view attributes, read with getattr(); declared for type checkers only.
    aggregation_name: str
    aggregation_serializer_class: type[BaseSerializer[Any]]
    aggregated_filterset_class: type[FilterSet]
    aggregated_filterset_fields: FilterFields
    aggregated_ordering_fields: Sequence[str] | Literal["__all__"]

    @action(methods=["get"], detail=False, url_path="aggregation", url_name="aggregation")
    def aggregation(self, request: Request) -> Response:
        queryset = self.filter_queryset(self.get_queryset())

        aggregator = Aggregator(request, queryset, self.get_aggregation_name())
        queryset = aggregator.get_aggregated_queryset()
        queryset = self.filter_aggregated_queryset(queryset)
        queryset = self.order_aggregated_queryset(queryset)

        context = {"request": request, "name": self.get_aggregation_name()}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_aggregation_serializer_class(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_aggregation_serializer_class(queryset, many=True, context=context)
        return Response(serializer.data)

    def get_aggregation_serializer_class(self, *args: Any, **kwargs: Any) -> BaseSerializer[Any]:
        serializer = getattr(self, "aggregation_serializer_class", None)
        if serializer is not None:
            return serializer(*args, **kwargs)
        return AggregationSerializer(*args, **kwargs)

    def get_aggregation_name(self) -> str:
        name = getattr(self, "aggregation_name", None)
        if isinstance(name, str):
            return name
        return "value"

    def filter_aggregated_queryset(self, queryset: QuerySet[Any, Any]) -> QuerySet[Any, Any]:
        filterset_class = getattr(self, "aggregated_filterset_class", None)
        if filterset_class is None:
            fields = getattr(self, "aggregated_filterset_fields", None) or []
            filterset_class = ValueFilter.with_filter_fields(fields, self.get_aggregation_name())
        helper_view = HelperView(filterset_class)
        queryset = DjangoFilterBackend().filter_queryset(self.request, queryset, helper_view)

        return queryset

    def order_aggregated_queryset(self, queryset: QuerySet[Any, Any]) -> QuerySet[Any, Any]:
        params = self.request.query_params.get("ordering")
        if params:
            fields = [param.strip() for param in params.split(",")]
            ordering = self.remove_invalid_ordering_fields(queryset, fields)
            if ordering:
                return queryset.order_by(*ordering)

        return queryset

    def remove_invalid_ordering_fields(self, queryset: QuerySet[Any, Any], fields: list[str]) -> list[str]:
        ordering_fields = getattr(self, "aggregated_ordering_fields", None) or getattr(self, "ordering_fields", None)
        if isinstance(ordering_fields, str) and ordering_fields != "__all__":
            ordering_fields = [ordering_fields]

        if not ordering_fields or ("__all__" in ordering_fields) or (ordering_fields == "__all__"):
            return fields

        def term_valid(term: str) -> bool:
            term = term.removeprefix("-")
            return term in ordering_fields

        return [term for term in fields if term_valid(term)]


class HelperView:
    def __init__(self, filterset_class: type[FilterSet]) -> None:
        self.filterset_class = filterset_class
