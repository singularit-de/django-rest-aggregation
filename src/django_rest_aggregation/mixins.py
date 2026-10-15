from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Literal

from django.db.models import QuerySet
from django_filters import FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from .aggregator import DEFAULT_MAX_GROUP_BY, Aggregator, AllowedFields
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
    aggregation_fields: AllowedFields
    aggregation_max_group_by: int | None

    @action(methods=["get"], detail=False, url_path="aggregation", url_name="aggregation")
    def aggregation(self, request: Request) -> Response:
        queryset = self.filter_queryset(self.get_queryset())

        aggregator = Aggregator(
            request,
            queryset,
            self.get_aggregation_name(),
            allowed_fields=self.get_aggregation_fields(),
            max_group_by=self.get_aggregation_max_group_by(),
        )
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

    def get_aggregation_fields(self) -> AllowedFields:
        """Fields allowed in group_by and aggregation_field (SEC-1).

        Defaults to the fields the view's serializer exposes for reading, so aggregation reveals nothing the
        normal API does not. ``aggregation_fields = "__all__"`` allows every model field and annotation.
        """
        fields = getattr(self, "aggregation_fields", None)
        if fields is not None:
            return fields
        serializer_fields = getattr(self.get_serializer(), "fields", {})
        return {
            field.source.replace(".", "__")
            for field in serializer_fields.values()
            if not field.write_only and field.source and field.source != "*"
        }

    def get_aggregation_max_group_by(self) -> int | None:
        """Maximum number of group_by fields (SEC-3); None means no limit."""
        return getattr(self, "aggregation_max_group_by", DEFAULT_MAX_GROUP_BY)

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
            # Only the result columns (group_by fields and the value) can be ordered by: other fields would
            # change the GROUP BY (BUG-1), leak hidden values (SEC-2) or be unknown (BUG-3). Others are ignored.
            columns = {*queryset.query.values_select, *queryset.query.annotation_select}
            fields = [term for term in fields if term.removeprefix("-") in columns]
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
