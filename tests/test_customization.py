from rest_framework.test import APITestCase

from tests.testapp.models import Author, Book


class TestCustomization(APITestCase):
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

    def test_custom_serializer_and_name(self):
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "sum", "aggregation_field": "price"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 10.55}])

        response = self.client.get(
            "/customized_book/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "price",
                "ordering": "CustomizedValue",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"], [{"group": "all", "CustomizedValue": "10.6"}])

    def test_pagination(self):
        response = self.client.get(
            "/customized_book/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "price",
                "ordering": "CustomizedValue",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.keys(), {"count", "next", "previous", "results"})

    def test_ordering_all_field(self):
        response = self.client.get(
            "/customized_book/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "price",
                "CustomizedValue__gte": 20,
                "ordering": "CustomizedValue",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"], [])

    def test_pagination_count(self):
        response = self.client.get(
            "/customized_book/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "price",
                "ordering": "CustomizedValue",
                "CustomizedValue__lte": 0,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)
