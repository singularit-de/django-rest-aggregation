from tests.base import AggregationTestCase, create_book
from tests.testapp.models import Author


class CustomizationTests(AggregationTestCase):
    @classmethod
    def setUpTestData(cls):
        author = Author.objects.create(name="John", age=20)
        create_book(1, author, 10.55, "4.5")

    def sum_price(self, **params):
        return self.get_rows(
            "customized_book", aggregation="sum", aggregation_field="price", ordering="CustomizedValue", **params
        )

    def test_default_serializer_and_name(self):
        rows = self.get_rows("book", aggregation="sum", aggregation_field="price")
        self.assertRows(rows, [{"group": "all", "value": 10.55}])

    def test_custom_serializer_and_name(self):
        self.assertEqual(self.sum_price(), [{"group": "all", "CustomizedValue": "10.6"}])

    def test_pagination(self):
        response = self.aggregate(
            "customized_book", aggregation="sum", aggregation_field="price", ordering="CustomizedValue"
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data.keys(), {"count", "next", "previous", "results"})
        self.assertEqual(response.data["count"], 1)

    def test_pagination_count_after_value_filter(self):
        response = self.aggregate(
            "customized_book",
            aggregation="sum",
            aggregation_field="price",
            ordering="CustomizedValue",
            CustomizedValue__lte=0,
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["count"], 0)

    def test_aggregated_filterset_fields_all(self):
        self.assertEqual(self.sum_price(CustomizedValue__gte=20), [])
        self.assertEqual(len(self.sum_price(CustomizedValue__lt=20)), 1)
