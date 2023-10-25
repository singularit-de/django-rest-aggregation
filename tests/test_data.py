BASIC_TESTING = [
(
        {"aggregation": "count", "group_by": "authors", "value__gte": 4},
        [
            {
                "authors": 1,
                "value": 3
            },
            {
                "authors": 2,
                "value": 4
            },
            {
                "authors": 3,
                "value": 4
            },
            {
                "authors": 4,
                "value": 4
            }
        ]
    ),
    (
        {"aggregation": "count"},
        [{'group': 'all', 'value': 15}]
    ),
    (
        {"aggregation": "sum", "aggregation_field": "price"},
        [{'group': 'all', 'value': 289.85}]
    ),
    (
        {"aggregation": "average", "aggregation_field": "price"},
        [{'group': 'all', 'value': 19.3233333333333}]
    ),
    (
        {"aggregation": "avg", "aggregation_field": "price"},
        [{'group': 'all', 'value': 19.3233333333333}]
    ),
    (
        {"aggregation": "minimum", "aggregation_field": "price"},
        [{'group': 'all', 'value': 15.99}]
    ),
    (
        {"aggregation": "min", "aggregation_field": "price"},
        [{'group': 'all', 'value': 15.99}]
    ),
    (
        {"aggregation": "maximum", "aggregation_field": "price"},
        [{'group': 'all', 'value': 23.99}]
    ),
    (
        {"aggregation": "max", "aggregation_field": "price"},
        [{'group': 'all', 'value': 23.99}]
    ),
]

GROUP_TESTING = [
    (
        {"aggregation": "count", "group_by": "authors"},
        [
            {
                "authors": 1,
                "value": 3
            },
            {
                "authors": 2,
                "value": 4
            },
            {
                "authors": 3,
                "value": 4
            },
            {
                "authors": 4,
                "value": 4
            }
        ]
    ),
    (
        {"aggregation": "avg", "group_by": "store", "aggregation_field": "price"},
        [
            {
                "store": 1,
                "value": 19.79
            },
            {
                "store": 2,
                "value": 20.19
            },
            {
                "store": 3,
                "value": 17.99
            }
        ]
    ),
    (
        {"aggregation": "count", "group_by": "authors,store"},
        [
            {
                "authors": 1,
                "store": 1,
                "value": 3
            },
            {
                "authors": 2,
                "store": 1,
                "value": 2
            },
            {
                "authors": 2,
                "store": 2,
                "value": 2
            },
            {
                "authors": 3,
                "store": 2,
                "value": 3
            },
            {
                "authors": 3,
                "store": 3,
                "value": 1
            },
            {
                "authors": 4,
                "store": 3,
                "value": 4
            }
        ]
    ),
]

EXCEPTION_TESTING = [
    (
        {},
        "'aggregation' is required"
    ),
    (
        {"aggregation": "noaggregation"},
        "'aggregation' must be one of ['average', 'avg', 'count', 'max', 'maximum', 'min', 'minimum', 'sum']"
    ),
    (
        {"aggregation": "sum"},
        "'aggregation_field' is required"
    ),
    (
        {"aggregation": "sum"},
        "'aggregation_field' is required"
    ),
    (
        {"aggregation": "sum", "aggregation_field": "no_aggregation_field"},
        "'aggregation_field' is not valid"
    ),
    (
        {"aggregation": "sum", "aggregation_field": "name"},
        "'aggregation_field' must be a number field"
    ),
    (
        {"aggregation": "max", "aggregation_field": "name"},
        "'aggregation_field' must be a number or date field"
    ),
    (
        {"aggregation": "count", "group_by": "not_a_group"},
        "'group_by' is not valid"
    )
]

# TODO add tests for paginated, filtered Queryset and AggregationViewSet
MISCELLANEOUS_TESTING = [
    # test annotated aggregation_field
    (
        {"aggregation": "max", "aggregation_field": "price_per_page"},
        [
            {
                "group": "all",
                "value": 0.06559375
            }
        ]
    ),
    # test annotated group_byField
    (
        {"aggregation": "count", "group_by": "expensive"},
        [
            {
                "expensive": 0,
                "value": 11
            },
            {
                "expensive": 1,
                "value": 4
            }
        ]
    )

]
