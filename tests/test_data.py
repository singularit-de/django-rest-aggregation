BASIC_TESTING = [
    (
        "/book/aggregation/",
        {"aggregation": "count"},
        [{'group': 'all', 'value': 15}]
    ),
    (
        "/book/aggregation/",
        {"aggregation": "sum", "aggregationField": "price"},
        [{'group': 'all', 'value': 289.85}]
    ),
    (
        "/book/aggregation/",
        {"aggregation": "average", "aggregationField": "price"},
        [{'group': 'all', 'value': 19.3233333333333}]
    ),
    (
        "/book/aggregation/",
        {"aggregation": "avg", "aggregationField": "price"},
        [{'group': 'all', 'value': 19.3233333333333}]
    ),
    (
        "/book/aggregation/",
        {"aggregation": "minimum", "aggregationField": "price"},
        [{'group': 'all', 'value': 15.99}]
    ),
    (
        "/book/aggregation/",
        {"aggregation": "min", "aggregationField": "price"},
        [{'group': 'all', 'value': 15.99}]
    ),
    (
        "/book/aggregation/",
        {"aggregation": "maximum", "aggregationField": "price"},
        [{'group': 'all', 'value': 23.99}]
    ),
    (
        "/book/aggregation/",
        {"aggregation": "max", "aggregationField": "price"},
        [{'group': 'all', 'value': 23.99}]
    ),
]

GROUP_TESTING = [
    (
        "/book/aggregation/",
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
        "/book/aggregation/",
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
        "/book/aggregation/",
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
        "/book/aggregation/",
        {},
        "'aggregation' is required"
    ),
    (
        "/book/aggregation/",
        {"aggregation": "noaggregation"},
        "'aggregation' must be one of ['average', 'avg', 'count', 'max', 'maximum', 'min', 'minimum', 'sum']"
    ),
    (
        "/book/aggregation/",
        {"aggregation": "sum"},
        "'aggregationField' is required"
    ),
    (
        "/book/aggregation/",
        {"aggregation": "sum"},
        "'aggregationField' is required"
    ),
    (
        "/book/aggregation/",
        {"aggregation": "sum", "aggregationField": "noaggregationfield"},
        "'aggregationField' is not valid"
    ),
    (
        "/book/aggregation/",
        {"aggregation": "sum", "aggregationField": "name"},
        "'aggregationField' must be a number field"
    ),
    (
        "/book/aggregation/",
        {"aggregation": "max", "aggregationField": "name"},
        "'aggregationField' must be a number or date field"
    ),
    (
        "/book/aggregation/",
        {"aggregation": "count", "aggregationGroupBy": "notagroup"},
        "'aggregationGroupBy' is not valid"
    )
]

# TODO add tests for paginated, filtered and AggregationViewSet
MISCELLANEOUS_TESTING = [

]
