from django.test import SimpleTestCase

from django_rest_aggregation.mixins import AggregationMixin
from tests.base import FilteringAndOrderingTestCase


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

    def test_multi_relation_ordering(self):
        response = self.client.get(
            "/book/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "pages",
                "group_by": "author__name,stores",
                "ordering": "author__agent__name,stores",
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
        # BUG-10: ordering_fields = "name" must not allow "na"
        view = AggregationMixin()
        view.ordering_fields = "name"
        self.assertEqual(view.remove_invalid_ordering_fields(None, ["na", "name", "-name"]), ["name", "-name"])
