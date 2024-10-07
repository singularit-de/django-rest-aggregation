from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.models import Case, When, Value
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request

from .enums import Aggregation


def get_filtered_params(request):
    params = {}
    for key in ["aggregation", "aggregation_field", "group_by"]:
        if len(request.query_params.getlist(key, [])) == 1:
            params[key] = request.query_params.getlist(key)[0]
        if len(request.query_params.getlist(key, [])) > 1:
            error_message = (
                f"Only one {key} is allowed" if key != "group_by" else "please use comma separated values for grouping"
            )
            raise ValidationError({"error": error_message})

    if params.get("group_by", None) is not None:
        params["group_by"] = params["group_by"].split(",")
    return params


def get_annotation(params, name):
    aggregation = params.get("aggregation")
    aggregation_field = params.get("aggregation_field")

    if aggregation in Aggregation.COUNT.value:
        return {name: models.Count("id")}

    if aggregation in Aggregation.SUM.value:
        return {name: models.Sum(aggregation_field)}

    if aggregation in Aggregation.AVERAGE.value:
        return {name: models.Avg(aggregation_field)}

    if aggregation in Aggregation.MIN.value:
        return {name: models.Min(aggregation_field)}

    if aggregation in Aggregation.MAX.value:
        return {name: models.Max(aggregation_field)}


def model_field_exists(field_name, model):
    fields = field_name.split("__")
    try:
        field = model._meta.get_field(fields[0])
        for field_name in fields[1:]:
            field = field.related_model._meta.get_field(field_name)
    except (FieldDoesNotExist, AttributeError):
        return False
    return True


def annotation_field_exists(field_name, queryset):
    return field_name in queryset.query.annotations


def field_exists(field_name, model, queryset):
    return model_field_exists(field_name, model) or annotation_field_exists(field_name, queryset)


def get_field_type(field_name, model, queryset):
    if annotation_field_exists(field_name, queryset):
        return queryset.query.annotations.get(field_name).output_field.get_internal_type()
    elif model_field_exists(field_name, model):
        fields = field_name.split("__")
        field = model._meta.get_field(fields[0])
        for field_name in fields[1:]:
            field = field.related_model._meta.get_field(field_name)
        return field.get_internal_type()


class Aggregator:
    def __init__(self, request: Request, queryset: models.QuerySet, aggregation_name: str):
        self.params = get_filtered_params(request)
        self.queryset = queryset
        self.model = queryset.model
        self.aggregation_name = aggregation_name

    def get_aggregated_queryset(self):
        self.validate_params()

        if (group_by := self.params.get("group_by", ["group"])) == ["group"]:
            self.queryset = self.queryset.annotate(group=Case(
                When(pk__isnull=False, then=Value("all")),
                default=Value("test")))

        return self.queryset.values(*group_by).annotate(**get_annotation(self.params, self.aggregation_name))

    def validate_params(self):
        # check if aggregation is in params and is valid
        if (aggregation := self.params.get("aggregation", None)) is None:
            raise ValidationError({"error": "'aggregation' is required"})
        if aggregation not in Aggregation.get_all_aggregations():
            raise ValidationError(
                {"error": f"'aggregation' must be one of {sorted(Aggregation.get_all_aggregations())}"}
            )

        # check if aggregation_field is in params and valid
        if aggregation in Aggregation.get_field_required_aggregations():
            if (aggregation_field := self.params.get("aggregation_field", None)) is None:
                raise ValidationError({"error": "'aggregation_field' is required"})
            if not field_exists(aggregation_field, self.model, self.queryset):
                raise ValidationError({"error": "'aggregation_field' is not valid"})

            # check if aggregation_field is correct type
            if aggregation in Aggregation.get_number_field_required_aggregations():
                if get_field_type(aggregation_field, self.model, self.queryset) not in [
                    "FloatField",
                    "IntegerField",
                    "DecimalField",
                ]:
                    raise ValidationError({"error": "'aggregation_field' must be a number field"})
            else:
                if get_field_type(aggregation_field, self.model, self.queryset) not in [
                    "FloatField",
                    "IntegerField",
                    "DecimalField",
                    "DateField",
                    "DateTimeField",
                ]:
                    raise ValidationError({"error": "'aggregation_field' must be a number or a date field"})

        # check if group_by is valid
        for group_by in self.params.get("group_by", []):
            if not field_exists(group_by, self.model, self.queryset):
                raise ValidationError({"error": "'group_by' is not valid"})
