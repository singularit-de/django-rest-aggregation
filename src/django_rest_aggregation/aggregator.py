from django.db import models
from rest_framework.request import Request

from django_rest_aggregation.enums import Aggregation


def validate_params(params):
    if params.get("aggregation", None) == "count":
        return True

    elif params("aggregation", None) in ["sum", "average", "minimum", "maximum"]:
        if params.get("aggregationField", None):
            return True

    return False


def get_filtered_params(request):
    params = {key: value for key, value in request.query_params.items() if
              key in ["aggregation", "aggregationField", "aggregationGroupBy"]}
    if validate_params(params):
        return params


def get_annotation(params):
    aggregation = params.get("aggregation")
    aggregation_field = params.get("aggregationField")

    if aggregation == Aggregation.COUNT:
        return {"value": models.Count('id')}

    if aggregation == Aggregation.SUM:
        return {"value": models.Sum(aggregation_field)}

    if aggregation == Aggregation.AVERAGE:
        return {"value": models.Avg(aggregation_field)}

    if aggregation == Aggregation.MIN:
        return {"value": models.Min(aggregation_field)}

    if aggregation == Aggregation.MAX:
        return {"value": models.Max(aggregation_field)}


def field_exists(field_name, queryset):
    return field_name in [i.__str__().split(".")[-1].replace('>', "") for i in queryset.model._meta.get_fields()]


class Aggregator:
    def __init__(self, request: Request):
        self.params = get_filtered_params(request)

    def aggregate_queryset(self, queryset):
        group_by = self.params.get("aggregationGroupBy", None)
        if field_exists(group_by, queryset):
            queryset = queryset.values(group_by)
        else:
            queryset = queryset.annotate(group=models.Value("all", output_field=models.CharField())).values("group")

        return queryset.annotate(**get_annotation(self.params))
