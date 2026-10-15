from django.db.models import Count
from django.test import SimpleTestCase
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from django_rest_aggregation.mixins import AggregationMixin
from tests.base import FilteringAndOrderingTestCase
from tests.testapp.models import Book


class TestOrdering(FilteringAndOrderingTestCase):
    def test_ordering_aggregation(self):
        # ordering by aggregation
        response = self.client.get(
            "/book/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "pages",
                "group_by": "author,stores",
                "ordering": "value",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            [
                {"author": self.author.pk, "stores": self.store.pk, "value": 400},
                {"author": self.author.pk, "stores": self.store2.pk, "value": 600},
                {"author": self.author2.pk, "stores": self.store.pk, "value": 1200},
                {"author": self.author2.pk, "stores": self.store2.pk, "value": 1400},
            ],
        )

        response = self.client.get(
            "/book/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "pages",
                "group_by": "author,stores",
                "ordering": "-value",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            [
                {"author": self.author2.pk, "stores": self.store2.pk, "value": 1400},
                {"author": self.author2.pk, "stores": self.store.pk, "value": 1200},
                {"author": self.author.pk, "stores": self.store2.pk, "value": 600},
                {"author": self.author.pk, "stores": self.store.pk, "value": 400},
            ],
        )

    def test_ordering(self):
        response = self.client.get(
            "/book/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "pages",
                "group_by": "author__name,stores",
                "ordering": "-author__name,stores",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            [
                {"author__name": "John", "stores": self.store.pk, "value": 400},
                {"author__name": "John", "stores": self.store2.pk, "value": 600},
                {"author__name": "Jane", "stores": self.store.pk, "value": 1200},
                {"author__name": "Jane", "stores": self.store2.pk, "value": 1400},
            ],
        )

    def test_ordering_by_multiple_fields(self):
        response = self.client.get(
            "/book/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "pages",
                "group_by": "author__name,stores",
                "ordering": "author__name,value",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            [
                {"author__name": "Jane", "stores": self.store.pk, "value": 1200},
                {"author__name": "Jane", "stores": self.store2.pk, "value": 1400},
                {"author__name": "John", "stores": self.store.pk, "value": 400},
                {"author__name": "John", "stores": self.store2.pk, "value": 600},
            ],
        )

        response = self.client.get(
            "/book/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "pages",
                "group_by": "author__name,stores",
                "ordering": "author__name,-value",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            [
                {"author__name": "Jane", "stores": self.store2.pk, "value": 1400},
                {"author__name": "Jane", "stores": self.store.pk, "value": 1200},
                {"author__name": "John", "stores": self.store2.pk, "value": 600},
                {"author__name": "John", "stores": self.store.pk, "value": 400},
            ],
        )

    def test_ordering_by_non_grouped_field_is_ignored(self):
        # author__agent__name is not a result column: ignored, so only "value" orders
        response = self.client.get(
            "/book/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "pages",
                "group_by": "author__name,stores",
                "ordering": "author__agent__name,value",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            [
                {"author__name": "John", "stores": self.store.pk, "value": 400},
                {"author__name": "John", "stores": self.store2.pk, "value": 600},
                {"author__name": "Jane", "stores": self.store.pk, "value": 1200},
                {"author__name": "Jane", "stores": self.store2.pk, "value": 1400},
            ],
        )


class TestOrderingFieldsAsString(SimpleTestCase):
    def test_string_ordering_fields_match_whole_names(self):
        # ordering_fields = "name" must not allow "na"
        view = AggregationMixin()
        view.ordering_fields = "name"
        view.request = Request(APIRequestFactory().get("/", {"ordering": "na,name,-name"}))
        queryset = Book.objects.values("name").annotate(value=Count("pk"))
        self.assertEqual(view.order_aggregated_queryset(queryset).query.order_by, ("name", "-name"))

    def test_list_ordering_fields_narrow_the_result_columns(self):
        # aggregated_ordering_fields can only remove result columns, never add other fields
        view = AggregationMixin()
        view.aggregated_ordering_fields = ["value", "pages"]
        view.request = Request(APIRequestFactory().get("/", {"ordering": "name,-value,pages"}))
        queryset = Book.objects.values("name").annotate(value=Count("pk"))
        self.assertEqual(view.order_aggregated_queryset(queryset).query.order_by, ("-value",))
