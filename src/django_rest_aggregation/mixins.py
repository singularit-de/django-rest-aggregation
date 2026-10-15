from __future__ import annotations

from collections.abc import Collection, Sequence
from typing import TYPE_CHECKING, Any, Literal

from django.apps import apps
from django.db.models import Model, QuerySet
from django_filters import FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from .aggregator import DEFAULT_MAX_GROUP_BY, Aggregator, AllowedFields, AllowedModels
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
    aggregation_models: Collection[type[Model] | str]
    aggregation_max_group_by: int | None

    @action(methods=["get"], detail=False, url_path="aggregation", url_name="aggregation")
    def aggregation(self, request: Request) -> Response:
        queryset = self.filter_queryset(self.get_queryset())

        aggregator = Aggregator(
            request,
            queryset,
            self.get_aggregation_name(),
            allowed_fields=self.get_aggregation_fields(),
            allowed_models=self.get_aggregation_models(),
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
        """Fields allowed in group_by and aggregation_field.

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

    def get_aggregation_models(self) -> AllowedModels:
        """Related models whose fields are allowed in group_by and aggregation_field, in addition to
        ``get_aggregation_fields()``.

        A relation path is allowed if every model it passes through after the view's model is listed, given as
        class or ``"app_label.ModelName"``. The view's model itself must be listed for paths that lead back to it.
        """
        listed = getattr(self, "aggregation_models", None) or ()
        return {apps.get_model(model) if isinstance(model, str) else model for model in listed}

    def get_aggregation_max_group_by(self) -> int | None:
        """Maximum number of group_by fields; None means no limit."""
        return getattr(self, "aggregation_max_group_by", DEFAULT_MAX_GROUP_BY)

    def filter_aggregated_queryset(self, queryset: QuerySet[Any, Any]) -> QuerySet[Any, Any]:
        filterset_class = getattr(self, "aggregated_filterset_class", None)
        if filterset_class is None:
            lookups = getattr(self, "aggregated_filterset_fields", None) or []
            filterset_class = ValueFilter.with_filter_fields(lookups, self.get_aggregation_name())
        helper_view = HelperView(filterset_class)
        queryset = DjangoFilterBackend().filter_queryset(self.request, queryset, helper_view)

        return queryset

    def order_aggregated_queryset(self, queryset: QuerySet[Any, Any]) -> QuerySet[Any, Any]:
        params = self.request.query_params.get("ordering")
        if not params:
            return queryset

        # Only result columns (group_by fields and the value): other fields would change the GROUP BY,
        # leak hidden values through the order, or be unknown. Terms outside are ignored.
        allowed = {*queryset.query.values_select, *queryset.query.annotation_select}
        # The view can narrow this down, never widen it.
        restriction = getattr(self, "aggregated_ordering_fields", None) or getattr(self, "ordering_fields", None)
        if isinstance(restriction, str):
            restriction = [restriction]
        if restriction and "__all__" not in restriction:
            allowed &= set(restriction)

        ordering = []
        for param in params.split(","):
            term = param.strip()
            if term.removeprefix("-") in allowed:
                ordering.append(term)

        return queryset.order_by(*ordering) if ordering else queryset


class HelperView:
    def __init__(self, filterset_class: type[FilterSet]) -> None:
        self.filterset_class = filterset_class
