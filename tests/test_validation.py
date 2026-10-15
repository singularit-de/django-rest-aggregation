from tests.base import AggregationTestCase, create_book
from tests.testapp.models import Author


class ValidationTests(AggregationTestCase):
    @classmethod
    def setUpTestData(cls):
        author = Author.objects.create(name="John", age=20)
        create_book(1, author, 10.55, "4.5")

    def assertErrors(self, cases):
        for params, error in cases:
            with self.subTest(**params):
                self.assertEqual(self.get_error("book", **params), error)

    def test_aggregation_validation(self):
        self.assertErrors(
            [
                ({}, "'aggregation' is required"),
                (
                    {"aggregation": "invalid"},
                    "'aggregation' must be one of "
                    "['average', 'avg', 'count', 'max', 'maximum', 'min', 'minimum', 'sum']",
                ),
                ({"aggregation": ["test", 123]}, "Only one aggregation is allowed"),
            ]
        )

    def test_aggregation_field_validation(self):
        self.assertErrors(
            [
                ({"aggregation": "sum"}, "'aggregation_field' is required"),
                ({"aggregation": "sum", "aggregation_field": "invalid"}, "'aggregation_field' is not valid"),
                ({"aggregation": "sum", "aggregation_field": ["test", 123]}, "Only one aggregation_field is allowed"),
                ({"aggregation": "sum", "aggregation_field": "name"}, "'aggregation_field' must be a number field"),
                (
                    {"aggregation": "max", "aggregation_field": "name"},
                    "'aggregation_field' must be a number or a date field",
                ),
            ]
        )

    def test_group_by_validation(self):
        self.assertErrors(
            [
                ({"aggregation": "count", "group_by": "invalid"}, "'group_by' is not valid"),
                (
                    {"aggregation": "count", "group_by": ["test", 123]},
                    "please use comma separated values for grouping",
                ),
            ]
        )

    def test_empty_aggregated_queryset(self):
        rows = self.get_rows("book", aggregation="count", group_by="author__name", value__gt=1)
        self.assertEqual(rows, [])
