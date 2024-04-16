from enum import Enum

from django.utils.translation import gettext_lazy as _


class Aggregation(Enum):
    COUNT = "count", _("count")
    SUM = "sum", _("sum")
    AVERAGE = "average", _("average"), "avg", _("avg")
    MIN = "minimum", _("minimum"), "min", _("min")
    MAX = "maximum", _("maximum"), "max", _("max")

    @classmethod
    def get_all_aggregations(cls):
        return {value for aggregation in cls for value in aggregation.value}

    @classmethod
    def get_field_required_aggregations(cls):
        return {value for aggregation in cls for value in aggregation.value if aggregation != cls.COUNT}

    @classmethod
    def get_number_field_required_aggregations(cls):
        return {
            value
            for aggregation in cls
            for value in aggregation.value
            if value not in {*cls.COUNT.value, *cls.MIN.value, *cls.MAX.value}
        }
