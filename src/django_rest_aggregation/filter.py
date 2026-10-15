from collections.abc import Sequence
from typing import ClassVar, Literal, cast

from django_filters import rest_framework as filters

FilterFields = Sequence[str] | Literal["__all__"]


def convert_to_filter_fields(fields: FilterFields, name: str) -> list[tuple[str, filters.NumberFilter]]:
    if fields == "__all__":
        fields = ["gte", "lte", "gt", "lt", "exact"]

    filtered_fields = []
    for field in fields:
        if isinstance(name, str):
            if field in ["gte", "lte", "gt", "lt"]:
                filtered_fields.append(
                    (
                        f"{name}__{field}",
                        filters.NumberFilter(field_name=name, lookup_expr=field),
                    )
                )
            if field == "exact":
                filtered_fields.append((f"{name}", filters.NumberFilter(field_name=name)))
    return filtered_fields


class ValueFilter(filters.FilterSet):
    # Set by django-filter's FilterSet metaclass; declared for type checkers.
    base_filters: ClassVar[dict[str, filters.Filter]]

    @classmethod
    def with_filter_fields(cls, fields: FilterFields, name: str) -> type["ValueFilter"]:
        """Return a subclass with the value filters, leaving this class unchanged."""
        return cast("type[ValueFilter]", type(cls.__name__, (cls,), dict(convert_to_filter_fields(fields, name))))

    @classmethod
    def set_filter_fields(cls, fields: FilterFields, name: str) -> None:
        filtered_fields = convert_to_filter_fields(fields, name)
        for field in filtered_fields:
            filter_name, filter_object = field
            cls.base_filters[filter_name] = filter_object
