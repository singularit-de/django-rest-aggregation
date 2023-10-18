from rest_framework.decorators import action
from rest_framework.response import Response

from .aggregator import Aggregator
from .serializers import AggregationSerializer


class AggregationMixin:
    @action(methods=['get'], detail=False, url_path='aggregation', url_name='aggregation')
    def aggregation(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        aggregator = Aggregator(request, queryset)
        queryset = aggregator.get_aggregated_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = AggregationSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = AggregationSerializer(queryset, many=True)
        return Response(serializer.data)
