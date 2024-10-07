from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response

from .aggregator import Aggregator
from .filter import ValueFilter
from .serializers import AggregationSerializer


class AggregationMixin:
    @action(methods=["get"], detail=False, url_path="aggregation", url_name="aggregation")
    def aggregation(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        aggregator = Aggregator(request, queryset, self.get_aggregation_name())
        queryset = aggregator.get_aggregated_queryset()
        queryset = self.filter_aggregated_queryset(queryset)
        queryset = self.order_aggregated_queryset(queryset)

        context = {
            "request": request,
            "name": self.get_aggregation_name()
        }
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_aggregation_serializer_class(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_aggregation_serializer_class(queryset, many=True, context=context)
        return Response(serializer.data)

    def get_aggregation_serializer_class(self, *args, **kwargs):
        serializer = getattr(self, "aggregation_serializer_class", None)
        if serializer is not None:
            return serializer(*args, **kwargs)
        return AggregationSerializer(*args, **kwargs)

    def get_aggregation_name(self):
        name = getattr(self, "aggregation_name", None)
        if isinstance(name, str):
            return name
        return "value"

    def filter_aggregated_queryset(self, queryset):
        if (fields := getattr(self, "aggregated_filterset_fields", None)) is not None:
            ValueFilter.set_filter_fields(fields, self.get_aggregation_name())
        filterset_class = getattr(self, "aggregated_filterset_class", ValueFilter)
        helper_view = HelperView(filterset_class)
        queryset = DjangoFilterBackend().filter_queryset(self.request, queryset, helper_view)

        return queryset

    def order_aggregated_queryset(self, queryset):
        params = self.request.query_params.get("ordering")
        if params:
            fields = [param.strip() for param in params.split(',')]
            ordering = self.remove_invalid_ordering_fields(queryset, fields)
            if ordering:
                return queryset.order_by(*ordering)

        return queryset

    def remove_invalid_ordering_fields(self, queryset, fields):
        ordering_fields = getattr(self, "aggregated_ordering_fields", None) or getattr(self, "ordering_fields", None)

        if not ordering_fields or ("__all__" in ordering_fields) or (ordering_fields == "__all__"):
            return fields

        def term_valid(term):
            if term.startswith("-"):
                term = term[1:]
            return term in ordering_fields

        return [term for term in fields if term_valid(term)]


class HelperView:
    def __init__(self, filterset_class):
        setattr(self, "filterset_class", filterset_class)
