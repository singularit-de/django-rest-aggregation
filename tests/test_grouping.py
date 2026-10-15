from tests.base import AggregationTestCase, create_book
from tests.testapp.models import Author, Store


class GroupingAndAnnotationTests(AggregationTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = Author.objects.create(name="John", age=20)
        cls.author2 = Author.objects.create(name="Jane", age=30)
        book1 = create_book(1, cls.author, 10.50, "4.5")
        book2 = create_book(2, cls.author, 12.49, "4.0")
        book3 = create_book(3, cls.author, 19.99, "3.5")
        book4 = create_book(4, cls.author2, 9.99, "3.0")
        book5 = create_book(5, cls.author2, 23.99, "2.5")

        Store.objects.create(name="Store1").books.set([book1, book3, book5])
        Store.objects.create(name="Store2").books.set([book2, book4])

    def test_group_by(self):
        rows = self.get_rows("book", aggregation="count", group_by="author")
        self.assertRows(
            rows,
            [
                {"author": self.author.pk, "value": 3},
                {"author": self.author2.pk, "value": 2},
            ],
            ordered=False,
        )

    def test_group_by_multiple_fields(self):
        rows = self.get_rows("book", aggregation="count", group_by="stores__name,author__name")
        self.assertRows(
            rows,
            [
                {"stores__name": "Store1", "author__name": "Jane", "value": 1},
                {"stores__name": "Store1", "author__name": "John", "value": 2},
                {"stores__name": "Store2", "author__name": "Jane", "value": 1},
                {"stores__name": "Store2", "author__name": "John", "value": 1},
            ],
            ordered=False,
        )

    def test_group_by_foreign_key_field(self):
        rows = self.get_rows("book", aggregation="count", group_by="author__name")
        self.assertRows(
            rows,
            [
                {"author__name": "Jane", "value": 2},
                {"author__name": "John", "value": 3},
            ],
            ordered=False,
        )

    def test_group_by_many_to_many_field(self):
        rows = self.get_rows(
            "store", aggregation="sum", aggregation_field="books__pages", group_by="books__author__age"
        )
        self.assertRows(
            rows,
            [
                {"books__author__age": 20, "value": 600},
                {"books__author__age": 30, "value": 900},
            ],
            ordered=False,
        )

    def test_aggregate_annotation(self):
        rows = self.get_rows("book", aggregation="sum", aggregation_field="price_per_page")
        self.assertRows(rows, [{"group": "all", "value": 0.3070383333333333}])

    def test_group_by_annotation(self):
        rows = self.get_rows("book", aggregation="avg", aggregation_field="price", group_by="expensive")
        self.assertRows(
            rows,
            [
                {"expensive": "expensive", "value": 21.99},
                {"expensive": "not expensive", "value": 10.993333333333334},
            ],
            ordered=False,
        )
