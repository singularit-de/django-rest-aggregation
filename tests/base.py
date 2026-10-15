import datetime
from decimal import Decimal

from django.urls import reverse
from rest_framework.test import APITestCase

from tests.testapp.models import Agent, Author, Book, Store


def create_book(number, author, price, rating):
    """Create ``Book<number>`` with ``number * 100`` pages, published on 2020-01-<number>."""
    return Book.objects.create(
        name=f"Book{number}",
        pages=number * 100,
        price=price,
        rating=Decimal(rating),
        author=author,
        pubdate=datetime.date(2020, 1, number),
    )


def normalize(value):
    # Float sums and averages differ in the last digits between databases.
    if isinstance(value, (float, Decimal)):
        return round(float(value), 6)
    return value


class AggregationTestCase(APITestCase):
    def aggregate(self, basename, **params):
        return self.client.get(reverse(f"{basename}-aggregation"), params)

    def get_rows(self, basename, **params):
        """Request an aggregation, check for 200 and return the rows (unwrapped if paginated)."""
        response = self.aggregate(basename, **params)
        self.assertEqual(response.status_code, 200, response.data)
        if isinstance(response.data, dict):
            return response.data["results"]
        return response.data

    def get_error(self, basename, **params):
        """Request an aggregation, check for 400 and return the error message."""
        response = self.aggregate(basename, **params)
        self.assertEqual(response.status_code, 400, response.data)
        return response.data["error"]

    def assertRows(self, rows, expected, *, ordered=True):
        """Compare result rows; ``ordered=False`` for results without a total ``ordering``."""
        rows = [{key: normalize(value) for key, value in row.items()} for row in rows]
        expected = [{key: normalize(value) for key, value in row.items()} for row in expected]
        if ordered:
            self.assertEqual(rows, expected)
        else:
            self.assertCountEqual(rows, expected)


class BookStoreTestCase(AggregationTestCase):
    """Two authors with agents, eight books and two stores, shared by filtering and ordering tests."""

    @classmethod
    def setUpTestData(cls):
        agent1 = Agent.objects.create(name="Adalbert Erl", address="Bookstreet 12")
        agent2 = Agent.objects.create(name="Balthasar König", address="Pagepassage 98")
        cls.author = Author.objects.create(name="John", age=20, agent=agent1)
        cls.author2 = Author.objects.create(name="Jane", age=30, agent=agent2)
        book1 = create_book(1, cls.author, 10.50, "4.5")
        book2 = create_book(2, cls.author, 12.49, "4.0")
        book3 = create_book(3, cls.author, 19.99, "3.5")
        book4 = create_book(4, cls.author, 9.99, "3.2")
        book5 = create_book(5, cls.author2, 23.99, "3.5")
        book6 = create_book(6, cls.author2, 20.99, "2.0")
        book7 = create_book(7, cls.author2, 16.00, "4.7")
        book8 = create_book(8, cls.author2, 28.99, "3.9")

        cls.store = Store.objects.create(name="Store1")
        cls.store.books.set([book1, book3, book5, book7])
        cls.store2 = Store.objects.create(name="Store2")
        cls.store2.books.set([book2, book4, book6, book8])

    def sum_pages_by_author_and_store(self, basename="book", **params):
        return self.get_rows(basename, aggregation="sum", aggregation_field="pages", group_by="author,stores", **params)
