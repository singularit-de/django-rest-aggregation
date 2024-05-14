from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response

from .aggregator import Aggregator
from .filter import ValueFilter
from .serializers import AggregationSerializer


class AggregationMixin:
    @action(methods=["get"], detail=False, url_path="aggregation", url_name="aggregation")
    def aggregation(self, request):
        queryset = self.get_queryset()

        if DjangoFilterBackend in self.filter_backends:
            queryset = DjangoFilterBackend().filter_queryset(request, queryset, self)

        aggregator = Aggregator(request, queryset, self.get_aggregation_name())
        filtered_queryset = self.filter_aggregated_queryset(aggregator.get_aggregated_queryset())

        context = {
            "request": request,
            "name": self.get_aggregation_name()
        }
        page = self.paginate_queryset(filtered_queryset)
        if page is not None:
            serializer = self.get_aggregation_serializer_class(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_aggregation_serializer_class(filtered_queryset, many=True, context=context)
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
        ordering_fields = getattr(self, "ordering_fields", [])
        valid_fields = queryset[0].keys()

        if ordering_fields == "__all__":
            ordering_fields = valid_fields
        else:
            ordering_fields = list(set(ordering_fields).intersection(set(queryset[0].keys())))

        if (fields := getattr(self, "aggregated_filterset_fields", None)) is not None:
            ValueFilter.set_filter_fields(fields, self.get_aggregation_name())
        filterset_class = getattr(self, "aggregated_filterset_class", ValueFilter)

        helper_view = HelperView(ordering_fields, filterset_class)

        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, helper_view)

        if not queryset.ordered:
            queryset = queryset.order_by(*valid_fields)

        return queryset


class HelperView:
    def __init__(self, ordering_fields, filterset_class):
        setattr(self, "ordering_fields", ordering_fields)
        setattr(self, "filterset_class", filterset_class)
