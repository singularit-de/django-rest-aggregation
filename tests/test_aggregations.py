import datetime

from tests.base import AggregationTestCase, create_book
from tests.testapp.models import Author


class BasicAggregationTests(AggregationTestCase):
    @classmethod
    def setUpTestData(cls):
        author = Author.objects.create(name="John", age=20)
        create_book(1, author, 10.50, "4.5")
        create_book(2, author, 12.49, "4.0")
        create_book(3, author, 19.99, "3.5")
        create_book(4, author, 9.99, "3.0")
        create_book(5, author, 23.99, "2.5")

    def assertAggregations(self, aggregation, cases):
        for field, expected in cases:
            with self.subTest(aggregation=aggregation, field=field):
                rows = self.get_rows("book", aggregation=aggregation, aggregation_field=field)
                self.assertRows(rows, [{"group": "all", "value": expected}])

    def test_count(self):
        rows = self.get_rows("book", aggregation="count")
        self.assertRows(rows, [{"group": "all", "value": 5}])

    def test_sum(self):
        self.assertAggregations("sum", [("pages", 1500), ("price", 76.96), ("rating", 17.5)])

    def test_avg(self):
        self.assertAggregations("avg", [("pages", 300), ("price", 15.392), ("rating", 3.5)])

    def test_minimum(self):
        self.assertAggregations(
            "minimum",
            [("pages", 100), ("price", 9.99), ("rating", 2.5), ("pubdate", datetime.date(2020, 1, 1))],
        )

    def test_maximum(self):
        self.assertAggregations(
            "maximum",
            [("pages", 500), ("price", 23.99), ("rating", 4.5), ("pubdate", datetime.date(2020, 1, 5))],
        )

    def test_aggregation_aliases(self):
        for aggregation, alias in [("average", "avg"), ("minimum", "min"), ("maximum", "max")]:
            with self.subTest(alias=alias):
                self.assertEqual(
                    self.get_rows("book", aggregation=alias, aggregation_field="pages"),
                    self.get_rows("book", aggregation=aggregation, aggregation_field="pages"),
                )

    def test_single_query(self):
        with self.assertNumQueries(1):
            self.get_rows("book", aggregation="sum", aggregation_field="pages")
