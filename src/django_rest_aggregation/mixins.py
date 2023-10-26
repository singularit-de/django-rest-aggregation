from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from .aggregator import Aggregator
from .filter import ValueFilter
from .serializers import AggregationSerializer


class AggregationMixin(GenericAPIView):
    @action(methods=['get'], detail=False, url_path="aggregation", url_name="aggregation")
    def aggregation(self, request):
        queryset = self.filter_queryset(self.get_queryset()).order_by()

        aggregator = Aggregator(request, queryset, self.get_aggregation_name())
        filtered_queryset = self.filter_aggregated_queryset(aggregator.get_aggregated_queryset())

        page = self.paginate_queryset(filtered_queryset)
        if page is not None:
            serializer = self.get_aggregation_serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_aggregation_serializer_class(filtered_queryset, many=True)
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
        if "__all__" in ordering_fields:
            ordering_fields = queryset[0].keys()
        elif ordering_fields is not []:
            ordering_fields = list(set(getattr(self, "ordering_fields", [])).intersection(set(queryset[0].keys())))

        if (fields := getattr(self, "aggregated_filtering_fields", None)) is not None:
            ValueFilter.set_filter_fields(fields, self.get_aggregation_name())
        filterset_class = getattr(self, "aggregated_filterset_class", ValueFilter)

        helper_view = HelperView(ordering_fields, filterset_class)
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, helper_view)
        return queryset


class HelperView:
    def __init__(self, ordering_fields, filterset_class):
        setattr(self, "ordering_fields", ordering_fields)
        setattr(self, "filterset_class", filterset_class)
