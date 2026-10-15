from rest_framework.test import APITestCase

from tests.testapp.models import Author, Book


class TestValidation(APITestCase):
    def setUp(self):
        self.author = Author(name="John", age=20)
        self.author.save()
        Book(
            name="Book1",
            pages=100,
            price=10.55,
            rating=4.5,
            author=self.author,
            pubdate="2020-01-01",
        ).save()

    def test_aggregation_validation(self):
        response = self.client.get("/book/aggregation/", {}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "'aggregation' is required")

        response = self.client.get("/book/aggregation/", {"aggregation": "invalid"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["error"],
            "'aggregation' must be one of ['average', 'avg', 'count', 'max', 'maximum', 'min', 'minimum', 'sum']",
        )

        response = self.client.get("/book/aggregation/", {"aggregation": ["test", 123]}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "Only one aggregation is allowed")

    def test_aggregation_field_validation(self):
        response = self.client.get("/book/aggregation/", {"aggregation": "sum"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "'aggregation_field' is required")

        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "sum", "aggregation_field": "invalid"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "'aggregation_field' is not valid")

        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "sum", "aggregation_field": ["test", 123]},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "Only one aggregation_field is allowed")

        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "sum", "aggregation_field": "name"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "'aggregation_field' must be a number field")

        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "max", "aggregation_field": "name"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["error"],
            "'aggregation_field' must be a number or a date field",
        )

    def test_group_by_validation(self):
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "count", "group_by": "invalid"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "'group_by' is not valid")

        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "count", "group_by": ["test", 123]},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "please use comma separated values for grouping")

    def test_empty_aggregated_queryset(self):
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "count", "group_by": "author__name", "value__gt": 1},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_aggregation_field_with_unresolvable_type(self):
        # BUG-12: annotation without a resolvable output_field gives 400, not 500
        response = self.client.get(
            "/publisher/aggregation/",
            {"aggregation": "sum", "aggregation_field": "mixed"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "'aggregation_field' must be a number field")
