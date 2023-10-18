from django.core.exceptions import FieldDoesNotExist
from django.db import models
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request

from django_rest_aggregation.enums import Aggregation


def get_filtered_params(request):
    params = {key: value for key, value in request.query_params.items() if
              key in ["aggregation", "aggregationField", "aggregationGroupBy"]}

    if params.get("aggregationGroupBy", None) is not None:
        params["aggregationGroupBy"] = params["aggregationGroupBy"].split(",")
    return params


def get_annotation(params):
    aggregation = params.get("aggregation")
    aggregation_field = params.get("aggregationField")

    if aggregation in Aggregation.COUNT.value:
        return {"value": models.Count('id')}

    if aggregation in Aggregation.SUM.value:
        return {"value": models.Sum(aggregation_field)}

    if aggregation in Aggregation.AVERAGE.value:
        return {"value": models.Avg(aggregation_field)}

    if aggregation in Aggregation.MIN.value:
        return {"value": models.Min(aggregation_field)}

    if aggregation in Aggregation.MAX.value:
        return {"value": models.Max(aggregation_field)}


def field_exists(field_name, model):
    fields = field_name.split("__")
    try:
        field = model._meta.get_field(fields[0])
        for field_name in fields[1:]:
            field = field.related_model._meta.get_field(field_name)
    except FieldDoesNotExist:
        return False
    return True


def get_field_type(field_name, model):
    fields = field_name.split("__")
    try:
        field = model._meta.get_field(fields[0])
        for field_name in fields[1:]:
            field = field.related_model._meta.get_field(field_name)
    except FieldDoesNotExist:
        return None
    return field.get_internal_type()


class Aggregator:
    def __init__(self, request: Request, queryset: models.QuerySet):
        self.params = get_filtered_params(request)
        self.queryset = queryset
        self.model = queryset.model

    def get_aggregated_queryset(self):
        self.validate_params()

        if (group_by := self.params.get("aggregationGroupBy", ["group"])) == ["group"]:
            self.queryset = self.queryset.annotate(group=models.Value("all", output_field=models.CharField()))

        return self.queryset.values(*group_by).annotate(**get_annotation(self.params))

    def validate_params(self):

        # check if aggregation is in params and is valid
        if (aggregation := self.params.get("aggregation", None)) is None:
            raise ValidationError({"error": "'aggregation' is required"})
        if aggregation not in Aggregation.get_all_aggregations():
            raise ValidationError(
                {"error": f"'aggregation' must be one of {sorted(Aggregation.get_all_aggregations())}"})

        # check if aggregationField is in params and valid
        if aggregation in Aggregation.get_field_required_aggregations():
            if (aggregation_field := self.params.get("aggregationField", None)) is None:
                raise ValidationError({"error": "'aggregationField' is required"})
            if not field_exists(aggregation_field, self.model):
                raise ValidationError(
                    {"error": f"'aggregationField' is not valid"})

            # check if aggregationField is correct type
            if aggregation in Aggregation.get_number_field_required_aggregations():
                if get_field_type(aggregation_field, self.model) not in ["FloatField", "IntegerField", "DecimalField"]:
                    raise ValidationError({"error": "'aggregationField' must be a number field"})
            else:
                if get_field_type(aggregation_field, self.model) not in ["FloatField", "IntegerField", "DecimalField",
                                                                         "DateField", "DateTimeField"]:
                    raise ValidationError({"error": "'aggregationField' must be a number or date field"})

        # check if aggregationGroupBy is valid
        for group_by in self.params.get("aggregationGroupBy", []):
            if not field_exists(group_by, self.model):
                raise ValidationError({"error": "'aggregationGroupBy' is not valid"})
