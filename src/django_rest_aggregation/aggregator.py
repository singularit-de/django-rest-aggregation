from typing import TYPE_CHECKING, Any, TypedDict

from django.core.exceptions import FieldDoesNotExist, FieldError
from django.db import models
from django.db.models import Case, Value, When
from django.db.models.fields.reverse_related import ForeignObjectRel
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request

from .enums import Aggregation

if TYPE_CHECKING:
    # Not imported at runtime: it needs django.contrib.contenttypes in INSTALLED_APPS.
    from django.contrib.contenttypes.fields import GenericForeignKey

NUMBER_FIELD_TYPES = {
    "FloatField",
    "DecimalField",
    "IntegerField",
    "BigIntegerField",
    "SmallIntegerField",
    "PositiveIntegerField",
    "PositiveBigIntegerField",
    "PositiveSmallIntegerField",
    "AutoField",
    "BigAutoField",
    "SmallAutoField",
}
DATE_FIELD_TYPES = {"DateField", "DateTimeField"}


class AggregationParams(TypedDict, total=False):
    aggregation: str
    aggregation_field: str
    group_by: list[str]


def get_filtered_params(request: Request) -> AggregationParams:
    raw: dict[str, str] = {}
    for key in ["aggregation", "aggregation_field", "group_by"]:
        if len(request.query_params.getlist(key, [])) == 1:
            raw[key] = request.query_params.getlist(key)[0]
        if len(request.query_params.getlist(key, [])) > 1:
            error_message = (
                f"Only one {key} is allowed" if key != "group_by" else "please use comma separated values for grouping"
            )
            raise ValidationError({"error": error_message})

    params = AggregationParams()
    if "aggregation" in raw:
        params["aggregation"] = raw["aggregation"]
    if "aggregation_field" in raw:
        params["aggregation_field"] = raw["aggregation_field"]
    if "group_by" in raw:
        params["group_by"] = [field.strip() for field in raw["group_by"].split(",")]
    return params


def get_annotation(params: AggregationParams, name: str) -> dict[str, models.Aggregate]:
    aggregation = params.get("aggregation")
    aggregation_field = params.get("aggregation_field")

    if aggregation in Aggregation.COUNT.value:
        return {name: models.Count("pk")}

    if aggregation in Aggregation.SUM.value:
        return {name: models.Sum(aggregation_field)}

    if aggregation in Aggregation.AVERAGE.value:
        return {name: models.Avg(aggregation_field)}

    if aggregation in Aggregation.MIN.value:
        return {name: models.Min(aggregation_field)}

    if aggregation in Aggregation.MAX.value:
        return {name: models.Max(aggregation_field)}

    # Unreachable after Aggregator.validate_params().
    raise ValueError(f"Unknown aggregation {aggregation!r}")


def get_model_field(
    field_name: str, model: type[models.Model]
) -> "models.Field[Any, Any] | ForeignObjectRel | GenericForeignKey":
    """Resolve a ``__``-separated field path; raises ``FieldDoesNotExist`` if a part is missing."""
    fields = field_name.split("__")
    field = model._meta.get_field(fields[0])
    for part in fields[1:]:
        related_model = field.related_model
        if not isinstance(related_model, type):
            # not a relation, so the path cannot continue
            raise FieldDoesNotExist(f"{field_name!r} is not a valid field path")
        field = related_model._meta.get_field(part)
    return field


def model_field_exists(field_name: str, model: type[models.Model]) -> bool:
    try:
        get_model_field(field_name, model)
    except FieldDoesNotExist:
        return False
    return True


def annotation_field_exists(field_name: str, queryset: models.QuerySet[Any, Any]) -> bool:
    return field_name in queryset.query.annotations


def field_exists(field_name: str, model: type[models.Model], queryset: models.QuerySet[Any, Any]) -> bool:
    return model_field_exists(field_name, model) or annotation_field_exists(field_name, queryset)


def get_field_type(field_name: str, model: type[models.Model], queryset: models.QuerySet[Any, Any]) -> str | None:
    if annotation_field_exists(field_name, queryset):
        try:
            return queryset.query.annotations[field_name].output_field.get_internal_type()
        except FieldError:
            # e.g. mixed types without an explicit output_field; rejected by the type check
            return None
    elif model_field_exists(field_name, model):
        return get_model_field(field_name, model).get_internal_type()
    return None


class Aggregator:
    def __init__(self, request: Request, queryset: models.QuerySet[Any, Any], aggregation_name: str) -> None:
        self.params = get_filtered_params(request)
        self.queryset = queryset
        self.model: type[models.Model] = queryset.model
        self.aggregation_name = aggregation_name

    def get_aggregated_queryset(self) -> models.QuerySet[Any, dict[str, Any]]:
        self.validate_params()

        if (group_by := self.params.get("group_by", ["group"])) == ["group"]:
            self.queryset = self.queryset.annotate(
                group=Case(When(pk__isnull=False, then=Value("all")), default=Value("test"))
            )

        return self.queryset.values(*group_by).annotate(**get_annotation(self.params, self.aggregation_name))

    def validate_params(self) -> None:
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
                if get_field_type(aggregation_field, self.model, self.queryset) not in NUMBER_FIELD_TYPES:
                    raise ValidationError({"error": "'aggregation_field' must be a number field"})
            else:
                if (
                    get_field_type(aggregation_field, self.model, self.queryset)
                    not in NUMBER_FIELD_TYPES | DATE_FIELD_TYPES
                ):
                    raise ValidationError({"error": "'aggregation_field' must be a number or a date field"})

        # check if group_by is valid
        for group_by in self.params.get("group_by", []):
            if not field_exists(group_by, self.model, self.queryset):
                raise ValidationError({"error": "'group_by' is not valid"})
