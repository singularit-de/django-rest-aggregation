from tests.base import BookStoreTestCase


class OrderingTests(BookStoreTestCase):
    def test_ordering_by_aggregation(self):
        ascending = [
            {"author": self.author.pk, "stores": self.store.pk, "value": 400},
            {"author": self.author.pk, "stores": self.store2.pk, "value": 600},
            {"author": self.author2.pk, "stores": self.store.pk, "value": 1200},
            {"author": self.author2.pk, "stores": self.store2.pk, "value": 1400},
        ]
        self.assertRows(self.sum_pages_by_author_and_store(ordering="value"), ascending)
        self.assertRows(self.sum_pages_by_author_and_store(ordering="-value"), ascending[::-1])

    def test_ordering_by_group_by_field(self):
        rows = self.get_rows(
            "book",
            aggregation="sum",
            aggregation_field="pages",
            group_by="author__name,stores",
            ordering="-author__name,stores",
        )
        self.assertRows(
            rows,
            [
                {"author__name": "John", "stores": self.store.pk, "value": 400},
                {"author__name": "John", "stores": self.store2.pk, "value": 600},
                {"author__name": "Jane", "stores": self.store.pk, "value": 1200},
                {"author__name": "Jane", "stores": self.store2.pk, "value": 1400},
            ],
        )

    def test_ordering_by_multiple_fields(self):
        jane = [
            {"author__name": "Jane", "stores": self.store.pk, "value": 1200},
            {"author__name": "Jane", "stores": self.store2.pk, "value": 1400},
        ]
        john = [
            {"author__name": "John", "stores": self.store.pk, "value": 400},
            {"author__name": "John", "stores": self.store2.pk, "value": 600},
        ]
        cases = [
            ("author__name,value", jane + john),
            ("author__name,-value", jane[::-1] + john[::-1]),
        ]
        for ordering, expected in cases:
            with self.subTest(ordering=ordering):
                rows = self.get_rows(
                    "book",
                    aggregation="sum",
                    aggregation_field="pages",
                    group_by="author__name,stores",
                    ordering=ordering,
                )
                self.assertRows(rows, expected)

    def test_ordering_by_related_field(self):
        rows = self.get_rows(
            "book",
            aggregation="sum",
            aggregation_field="pages",
            group_by="author__name,stores",
            ordering="author__agent__name,stores",
        )
        self.assertRows(
            rows,
            [
                {"author__name": "John", "stores": self.store.pk, "value": 400},
                {"author__name": "John", "stores": self.store2.pk, "value": 600},
                {"author__name": "Jane", "stores": self.store.pk, "value": 1200},
                {"author__name": "Jane", "stores": self.store2.pk, "value": 1400},
            ],
        )
