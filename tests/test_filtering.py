from django_rest_aggregation.filter import ValueFilter
from tests.base import FilteringAndOrderingTestCase


class TestFiltering(FilteringAndOrderingTestCase):
    def test_filter_before_aggregation(self):
        # filtering before aggregation
        response = self.client.get(
            "/book/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "pages",
                "author__name": self.author.name,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 1000}])

        response = self.client.get(
            "/book/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "pages",
                "author__name": self.author2.name,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 2600}])

        # filtering after aggregation
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "sum", "aggregation_field": "pages", "pages__gt": 200},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 3300}])

    def test_aggregated_filterset_fields(self):
        # value__lte
        response = self.client.get(
            "/book/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "pages",
                "group_by": "author,stores",
                "ordering": "author,stores",
                "value__lte": 1000,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            [
                {"author": self.author.pk, "stores": self.store.pk, "value": 400},
                {"author": self.author.pk, "stores": self.store2.pk, "value": 600},
            ],
        )

        # value__gte
        response = self.client.get(
            "/book/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "pages",
                "group_by": "author,stores",
                "ordering": "author,stores",
                "value__gte": 1000,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            [
                {"author": self.author2.pk, "stores": self.store.pk, "value": 1200},
                {"author": self.author2.pk, "stores": self.store2.pk, "value": 1400},
            ],
        )

        # value__lt
        response = self.client.get(
            "/book/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "pages",
                "group_by": "author,stores",
                "ordering": "author,stores",
                "value__lt": 1200,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            [
                {"author": self.author.pk, "stores": self.store.pk, "value": 400},
                {"author": self.author.pk, "stores": self.store2.pk, "value": 600},
            ],
        )

        # value__gt
        response = self.client.get(
            "/book/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "pages",
                "group_by": "author,stores",
                "value__gt": 1400,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

        # value exact
        response = self.client.get(
            "/book/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "pages",
                "group_by": "author,stores",
                "value": 1200,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            [{"author": self.author2.pk, "stores": self.store.pk, "value": 1200}],
        )

    def test_aggregated_filterset_class(self):
        # only value__gte and value__lte are allowed
        response = self.client.get(
            "/author/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "books__pages",
                "group_by": "name",
                "test123__gte": 2600,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"name": "Jane", "test123": 2600}])

    def test_aggregated_filterset_class_ignored_fields(self):
        # value__gt and value__lt are not specified in the filter
        response = self.client.get(
            "/author/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "books__pages",
                "group_by": "name",
                "test123__lte": 1500,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"name": "John", "test123": 1000}])

        response = self.client.get(
            "/author/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "books__pages",
                "group_by": "name",
                "ordering": "name",
                "test123__gt": 2600,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            [{"name": "Jane", "test123": 2600}, {"name": "John", "test123": 1000}],
        )

    def test_value_filters_do_not_leak_between_views(self):
        # value filters of one view must not show up in another view
        response = self.client.get(
            "/customized_book/aggregation/",
            {"aggregation": "sum", "aggregation_field": "price", "CustomizedValue__gte": 0},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ValueFilter.base_filters, {})

        response = self.client.get(
            "/store/aggregation/",
            {"aggregation": "count", "CustomizedValue__gt": 0},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 2}])
