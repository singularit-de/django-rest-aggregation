from rest_framework.decorators import action
from rest_framework.response import Response

from .aggregator import Aggregator
from .serializers import AggregationSerializer


class AggregationMixin:
    @action(methods=['get'], detail=False, url_path='aggregation', url_name='aggregation')
    def aggregation(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        aggregator = Aggregator(request, queryset, self.get_aggregation_name())
        queryset = aggregator.get_aggregated_queryset()
        queryset = self.filter_aggregated_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_aggregation_serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_aggregation_serializer_class(queryset, many=True)
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

    # Todo
    def filter_aggregated_queryset(self, queryset):
        class HelperClass:
            def __init__(self, ordering_fields, filterset_class, filterset_fields):
                setattr(self, "ordering_fields", ordering_fields)
                setattr(self, "filterset_class", filterset_class)
                setattr(self, "filterset_fields", filterset_fields)

        filter_dict = {
            "ordering_fields": getattr(self, "ordering_fields", None),
            "filterset_class": getattr(self, "aggregated_filterset_class", None),
            "filterset_fields": getattr(self, "aggregated_filterset_fields", None)
        }
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, HelperClass(**filter_dict))
        return queryset
#
