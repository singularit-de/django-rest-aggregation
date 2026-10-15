from tests.base import BookStoreTestCase


class FilteringTests(BookStoreTestCase):
    def test_filter_before_aggregation(self):
        cases = [
            ({"author__name": "John"}, 1000),
            ({"author__name": "Jane"}, 2600),
            ({"pages__gt": 200}, 3300),
        ]
        for params, expected in cases:
            with self.subTest(**params):
                rows = self.get_rows("book", aggregation="sum", aggregation_field="pages", **params)
                self.assertRows(rows, [{"group": "all", "value": expected}])

    def test_aggregated_filterset_fields(self):
        john_store1 = {"author": self.author.pk, "stores": self.store.pk, "value": 400}
        john_store2 = {"author": self.author.pk, "stores": self.store2.pk, "value": 600}
        jane_store1 = {"author": self.author2.pk, "stores": self.store.pk, "value": 1200}
        jane_store2 = {"author": self.author2.pk, "stores": self.store2.pk, "value": 1400}
        cases = [
            ({"value__lte": 1000}, [john_store1, john_store2]),
            ({"value__gte": 1000}, [jane_store1, jane_store2]),
            ({"value__lt": 1200}, [john_store1, john_store2]),
            ({"value__gt": 1400}, []),
            ({"value": 1200}, [jane_store1]),
        ]
        for params, expected in cases:
            with self.subTest(**params):
                self.assertRows(self.sum_pages_by_author_and_store(**params), expected, ordered=False)

    def test_aggregated_filterset_class(self):
        rows = self.get_rows(
            "author", aggregation="sum", aggregation_field="books__pages", group_by="name", test123__gte=2600
        )
        self.assertRows(rows, [{"name": "Jane", "test123": 2600}])

        rows = self.get_rows(
            "author", aggregation="sum", aggregation_field="books__pages", group_by="name", test123__lte=1500
        )
        self.assertRows(rows, [{"name": "John", "test123": 1000}])

    def test_aggregated_filterset_class_ignores_undeclared_filters(self):
        # Test123Filter only declares test123__gte and test123__lte.
        rows = self.get_rows(
            "author", aggregation="sum", aggregation_field="books__pages", group_by="name", test123__gt=2600
        )
        self.assertRows(rows, [{"name": "Jane", "test123": 2600}, {"name": "John", "test123": 1000}], ordered=False)
