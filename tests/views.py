from src.drf_aggregation.filters import ColumnIndexFilter
from src.drf_aggregation.filters import TruncateDateFilter
from src.drf_aggregation import AggregationViewSet
from rest_framework.filters import SearchFilter

from .models import TestCaseModel


class TestCaseViewSet(AggregationViewSet):
    queryset = TestCaseModel.objects.all()
    filter_backends = [SearchFilter, TruncateDateFilter, ColumnIndexFilter]
    search_fields = ["group1"]
