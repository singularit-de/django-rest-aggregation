import datetime

from django.db import connection
from rest_framework.test import APITestCase

from tests.testapp.models import Author, Book, Publisher


class TestBasicFunctionality(APITestCase):
    def setUp(self):
        author = Author(name="John", age=20)
        author.save()
        Book(
            name="Book1",
            pages=100,
            price=10.50,
            rating=4.5,
            author=author,
            pubdate="2020-01-01",
        ).save()
        Book(
            name="Book2",
            pages=200,
            price=12.49,
            rating=4.0,
            author=author,
            pubdate="2020-01-02",
        ).save()
        Book(
            name="Book3",
            pages=300,
            price=19.99,
            rating=3.5,
            author=author,
            pubdate="2020-01-03",
        ).save()
        Book(
            name="Book4",
            pages=400,
            price=9.99,
            rating=3.0,
            author=author,
            pubdate="2020-01-04",
        ).save()
        Book(
            name="Book5",
            pages=500,
            price=23.99,
            rating=2.5,
            author=author,
            pubdate="2020-01-05",
        ).save()

    def test_database(self):
        print("\n--- Database ---")
        print(connection.vendor)
        if connection.vendor != "microsoft":
            print(connection.get_database_version())
        print("----------------\n")

    def test_count(self):
        response = self.client.get("/book/aggregation/", {"aggregation": "count"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 5}])

    def test_sum(self):
        # Sum of IntegerField
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "sum", "aggregation_field": "pages"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 1500}])

        # Sum of FloatField
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "sum", "aggregation_field": "price"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["group"], "all")
        self.assertAlmostEqual(response.data[0]["value"], 76.96)

        # Sum of DecimalField
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "sum", "aggregation_field": "rating"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 17.5}])

    def test_avg(self):
        # Avg of IntegerField
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "avg", "aggregation_field": "pages"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 300}])

        # Avg of FloatField
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "avg", "aggregation_field": "price"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["group"], "all")
        self.assertAlmostEqual(response.data[0]["value"], 15.392)

        # Avg of DecimalField
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "avg", "aggregation_field": "rating"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 3.5}])

    def test_minimum(self):
        # Minimum of IntegerField
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "minimum", "aggregation_field": "pages"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 100}])

        # Minimum of FloatField
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "minimum", "aggregation_field": "price"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 9.99}])

        # Minimum of DecimalField
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "minimum", "aggregation_field": "rating"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 2.5}])

        # Minimum of DateField
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "minimum", "aggregation_field": "pubdate"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": datetime.date(2020, 1, 1)}])

    def test_maximum(self):
        # Maximum of IntegerField
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "maximum", "aggregation_field": "pages"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 500}])

        # Maximum of FloatField
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "maximum", "aggregation_field": "price"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 23.99}])

        # Maximum of DecimalField
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "maximum", "aggregation_field": "rating"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 4.5}])

        # Maximum of DateField
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "maximum", "aggregation_field": "pubdate"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": datetime.date(2020, 1, 5)}])


class TestFieldTypes(APITestCase):
    def setUp(self):
        Publisher(code="P1", name="Penguin", revenue=3_000_000_000, employees=100, founded=1935).save()
        Publisher(code="P2", name="Pagepress", revenue=2_000_000_000, employees=50, founded=1990).save()

    def test_count_with_primary_key_not_named_id(self):
        # BUG-4
        response = self.client.get("/publisher/aggregation/", {"aggregation": "count"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 2}])

    def test_integer_field_variants(self):
        # BUG-5: BigIntegerField, PositiveIntegerField, SmallIntegerField
        cases = [
            ("sum", "revenue", 5_000_000_000),
            ("sum", "employees", 150),
            ("avg", "founded", 1962.5),
            ("max", "employees", 100),
            ("min", "founded", 1935),
        ]
        for aggregation, field, expected in cases:
            with self.subTest(aggregation=aggregation, field=field):
                response = self.client.get(
                    "/publisher/aggregation/",
                    {"aggregation": aggregation, "aggregation_field": field},
                    format="json",
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.data), 1)
                self.assertAlmostEqual(response.data[0]["value"], expected)
