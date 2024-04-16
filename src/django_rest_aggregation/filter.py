from django_filters import rest_framework as filters


def convert_to_filter_fields(fields, name):
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
    @classmethod
    def set_filter_fields(cls, fields, name):
        filtered_fields = convert_to_filter_fields(fields, name)
        for field in filtered_fields:
            filter_name, filter_object = field
            cls.base_filters[filter_name] = filter_object
