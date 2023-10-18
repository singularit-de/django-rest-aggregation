from parameterized import parameterized
from rest_framework.test import APITestCase

from .fixture import AUTHORS, BOOKS, PUBLISHERS, STORES
from .models import Book, Author, Publisher, Store
from .test_data import BASIC_TESTING, GROUP_TESTING, EXCEPTION_TESTING


class AggregationTests(APITestCase):
    def setUp(self):
        for author_data in AUTHORS:
            author = Author(**author_data)
            author.save()
        for publisher_data in PUBLISHERS:
            publisher = Publisher(**publisher_data)
            publisher.save()

        for book_data in BOOKS:
            book_data = book_data.copy()
            authors_data = book_data.pop("authors", [])
            publisher_data = book_data.pop("publisher", [])
            book = Book(**book_data, publisher_id=publisher_data)
            book.save()
            book.authors.set(authors_data)

        for store in STORES:
            store = store.copy()
            books_data = store.pop("books", [])
            store = Store(**store)
            store.save()
            store.books.set(books_data)

    @parameterized.expand(BASIC_TESTING + GROUP_TESTING)
    def test_200(self, url, query, expected_response):
        response = self.client.get(url, query, format="json")
        self.assertEqual(response.status_code, 200, msg=f"Failed on: {query}")
        self.assertEqual(response.data, expected_response,
                         msg=f"Failed on: {query}"
                             f"\nResponse: {response.data}"
                             f"\nExpected: {expected_response}")

    @parameterized.expand(EXCEPTION_TESTING)
    def test_400(self, url, query, expected_response):
        response = self.client.get(url, query, format="json")
        self.assertEqual(response.status_code, 400, msg=f"Failed on: {query}")
        self.assertEqual(response.data['error'], expected_response,
                         msg=f"Failed on: {query}"
                             f"\nResponse: {response.data['error']}"
                             f"\nExpected: {expected_response}")
