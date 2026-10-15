from __future__ import annotations

from collections.abc import Sequence
from typing import ClassVar, Literal, cast

from django_filters import rest_framework as filters

# Value of aggregated_filterset_fields: lookups such as ["gte", "lt"], or "__all__".
FilterFields = Sequence[str] | Literal["__all__"]

COMPARISON_LOOKUPS = ["gte", "lte", "gt", "lt"]
ALL_LOOKUPS = [*COMPARISON_LOOKUPS, "exact"]


def convert_to_filter_fields(lookups: FilterFields, name: str) -> list[tuple[str, filters.NumberFilter]]:
    """Build the value filters for the aggregated value ``name`` as (query parameter, filter) pairs.

    ``["gte", "exact"]`` with name ``"value"`` gives ``value__gte`` (value >= x) and ``value`` (value = x).
    Unknown lookups are ignored.
    """
    if lookups == "__all__":
        lookups = ALL_LOOKUPS

    value_filters = []
    for lookup in lookups:
        if lookup in COMPARISON_LOOKUPS:
            value_filters.append((f"{name}__{lookup}", filters.NumberFilter(field_name=name, lookup_expr=lookup)))
        elif lookup == "exact":
            value_filters.append((name, filters.NumberFilter(field_name=name)))
    return value_filters


class ValueFilter(filters.FilterSet):
    # Set by django-filter's FilterSet metaclass; declared for type checkers.
    base_filters: ClassVar[dict[str, filters.Filter]]

    @classmethod
    def with_filter_fields(cls, lookups: FilterFields, name: str) -> type[ValueFilter]:
        """Return a subclass with the value filters, leaving this class unchanged.

        The filter names depend on the view (e.g. ``value__gte``), so the subclass is created at runtime.
        Filters passed as class attributes are collected by django-filter's FilterSet metaclass into the
        subclass's own ``base_filters``.
        """
        value_filters = dict(convert_to_filter_fields(lookups, name))
        subclass = type(cls.__name__, (cls,), value_filters)
        # type() is typed as returning a plain ``type``; it is a subclass of this class.
        return cast(type[ValueFilter], subclass)
