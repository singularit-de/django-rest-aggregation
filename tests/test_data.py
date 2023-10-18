BASIC_TESTING = [
    (
        {"aggregation": "count"},
        [{'group': 'all', 'value': 15}]
    ),
    (
        {"aggregation": "sum", "aggregationField": "price"},
        [{'group': 'all', 'value': 289.85}]
    ),
    (
        {"aggregation": "average", "aggregationField": "price"},
        [{'group': 'all', 'value': 19.3233333333333}]
    ),
    (
        {"aggregation": "avg", "aggregationField": "price"},
        [{'group': 'all', 'value': 19.3233333333333}]
    ),
    (
        {"aggregation": "minimum", "aggregationField": "price"},
        [{'group': 'all', 'value': 15.99}]
    ),
    (
        {"aggregation": "min", "aggregationField": "price"},
        [{'group': 'all', 'value': 15.99}]
    ),
    (
        {"aggregation": "maximum", "aggregationField": "price"},
        [{'group': 'all', 'value': 23.99}]
    ),
    (
        {"aggregation": "max", "aggregationField": "price"},
        [{'group': 'all', 'value': 23.99}]
    ),
]

GROUP_TESTING = [
    (
        {"aggregation": "count", "aggregationGroupBy": "authors"},
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
        {"aggregation": "avg", "aggregationGroupBy": "store", "aggregationField": "price"},
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
        {"aggregation": "count", "aggregationGroupBy": "authors,store"},
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
        "'aggregationField' is required"
    ),
    (
        {"aggregation": "sum"},
        "'aggregationField' is required"
    ),
    (
        {"aggregation": "sum", "aggregationField": "noaggregationfield"},
        "'aggregationField' is not valid"
    ),
    (
        {"aggregation": "sum", "aggregationField": "name"},
        "'aggregationField' must be a number field"
    ),
    (
        {"aggregation": "max", "aggregationField": "name"},
        "'aggregationField' must be a number or date field"
    ),
    (
        {"aggregation": "count", "aggregationGroupBy": "notagroup"},
        "'aggregationGroupBy' is not valid"
    )
]

# TODO add tests for paginated, filtered Queryset and AggregationViewSet
MISCELLANEOUS_TESTING = [
    # test annotated aggregationField
    (
        {"aggregation": "max", "aggregationField": "price_per_page"},
        [
            {
                "group": "all",
                "value": 0.06559375
            }
        ]
    ),
    # test annotated aggregationGroupByField
    (
        {"aggregation": "count", "aggregationGroupBy": "expensive"},
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
