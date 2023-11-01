from rest_framework.test import APITestCase

from tests.models import Author, Book, Store


# class AggregationTests(APITestCase):
#    def setUp(self):
#        for author_data in AUTHORS:
#            author = Author(**author_data)
#            author.save()
#        for publisher_data in PUBLISHERS:
#            publisher = Publisher(**publisher_data)
#            publisher.save()
#
#        for book_data in BOOKS:
#            book_data = book_data.copy()
#            authors_data = book_data.pop("authors", [])
#            publisher_data = book_data.pop("publisher", [])
#            book = Book(**book_data, publisher_id=publisher_data)
#            book.save()
#            book.authors.set(authors_data)
#
#        for store in STORES:
#            store = store.copy()
#            books_data = store.pop("books", [])
#            store = Store(**store)
#            store.save()
#            store.books.set(books_data)
#
#        self.URL = "/book/aggregation/"
#
#    @parameterized.expand(BASIC_TESTING + GROUP_TESTING + MISCELLANEOUS_TESTING)
#    def test_200(self, query, expected_response):
#        response = self.client.get(self.URL, query, format="json")
#        self.assertEqual(response.status_code, 200, msg=f"Failed on: {query}")
#        self.assertEqual(response.data, expected_response,
#                         msg=f"Failed on: {query}"
#                             f"\nResponse: {response.data}"
#                             f"\nExpected: {expected_response}")
#
#    @parameterized.expand(EXCEPTION_TESTING)
#    def test_400(self, query, expected_response):
#        response = self.client.get(self.URL, query, format="json")
#        self.assertEqual(response.status_code, 400, msg=f"Failed on: {query}")
#        self.assertEqual(response.data['error'], expected_response,
#                         msg=f"Failed on: {query}"
#                             f"\nResponse: {response.data['error']}"
#                             f"\nExpected: {expected_response}")

class TestBasicFunctionality(APITestCase):
    def setUp(self):
        author = Author(name="John", age=20)
        author.save()
        Book(name="Book1", pages=100, price=10.50, rating=4.5, author=author, pubdate="2020-01-01").save()
        Book(name="Book2", pages=200, price=12.49, rating=4.0, author=author, pubdate="2020-01-02").save()
        Book(name="Book3", pages=300, price=19.99, rating=3.5, author=author, pubdate="2020-01-03").save()
        Book(name="Book4", pages=400, price=9.99, rating=3.0, author=author, pubdate="2020-01-04").save()
        Book(name="Book5", pages=500, price=23.99, rating=2.5, author=author, pubdate="2020-01-05").save()

    def test_count(self):
        response = self.client.get("/book/aggregation/", {"aggregation": "count"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 5}])

    def test_sum(self):
        # Sum of IntegerField
        response = self.client.get("/book/aggregation/", {"aggregation": "sum", "aggregation_field": "pages"},
                                   format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 1500}])

        # Sum of FloatField
        response = self.client.get("/book/aggregation/", {"aggregation": "sum", "aggregation_field": "price"},
                                   format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 76.96000000000001}])

        # Sum of DecimalField
        response = self.client.get("/book/aggregation/", {"aggregation": "sum", "aggregation_field": "rating"},
                                   format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 17.5}])

    def test_avg(self):
        # Avg of IntegerField
        response = self.client.get("/book/aggregation/", {"aggregation": "avg", "aggregation_field": "pages"},
                                   format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 300}])

        # Avg of FloatField
        response = self.client.get("/book/aggregation/", {"aggregation": "avg", "aggregation_field": "price"},
                                   format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 15.392000000000001}])

        # Avg of DecimalField
        response = self.client.get("/book/aggregation/", {"aggregation": "avg", "aggregation_field": "rating"},
                                   format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 3.5}])

    def test_minimum(self):
        # Minimum of IntegerField
        response = self.client.get("/book/aggregation/", {"aggregation": "minimum", "aggregation_field": "pages"},
                                   format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 100}])

        # Minimum of FloatField
        response = self.client.get("/book/aggregation/", {"aggregation": "minimum", "aggregation_field": "price"},
                                   format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 9.99}])

        # Minimum of DecimalField
        response = self.client.get("/book/aggregation/", {"aggregation": "minimum", "aggregation_field": "rating"},
                                   format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 2.5}])

        # Minimum of DateField
        response = self.client.get("/book/aggregation/", {"aggregation": "minimum", "aggregation_field": "pubdate"},
                                   format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": "2020-01-01"}])

    def test_maximum(self):
        # Maximum of IntegerField
        response = self.client.get("/book/aggregation/", {"aggregation": "maximum", "aggregation_field": "pages"},
                                   format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 500}])

        # Maximum of FloatField
        response = self.client.get("/book/aggregation/", {"aggregation": "maximum", "aggregation_field": "price"},
                                   format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 23.99}])

        # Maximum of DecimalField
        response = self.client.get("/book/aggregation/", {"aggregation": "maximum", "aggregation_field": "rating"},
                                   format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 4.5}])

        # Maximum of DateField
        response = self.client.get("/book/aggregation/", {"aggregation": "maximum", "aggregation_field": "pubdate"},
                                   format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": "2020-01-05"}])


class TestGroupingAndAnnotations(APITestCase):
    def setUp(self):
        self.author = Author(name="John", age=20)
        self.author.save()
        self.author2 = Author(name="Jane", age=30)
        self.author2.save()

        Book(name="Book1", pages=100, price=10.50, rating=4.5, author=self.author, pubdate="2020-01-01").save()
        Book(name="Book2", pages=200, price=12.49, rating=4.0, author=self.author, pubdate="2020-01-02").save()
        Book(name="Book3", pages=300, price=19.99, rating=3.5, author=self.author, pubdate="2020-01-03").save()
        Book(name="Book4", pages=400, price=09.99, rating=3.0, author=self.author2, pubdate="2020-01-04").save()
        Book(name="Book5", pages=500, price=23.99, rating=2.5, author=self.author2, pubdate="2020-01-05").save()

        store = Store(name="Store1")
        store.save()
        store.books.set([1, 3, 5])

        store = Store(name="Store2")
        store.save()
        store.books.set([2, 4])

    def test_group_by(self):
        # Simple Group by
        response = self.client.get("/book/aggregation/", {"aggregation": "count", "group_by": "author"},
                                   format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data,
                         [{"author": self.author.pk, "value": 3}, {"author": self.author2.pk, "value": 2}])

        # Group by foreign key related field
        response = self.client.get("/book/aggregation/", {"aggregation": "count", "group_by": "author__name"},
                                   format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"author__name": self.author2.name, "value": 2},
                                         {"author__name": self.author.name, "value": 3}])

        # Group by many to many related field
        resonse = self.client.get("/store/aggregation/",
                                  {"aggregation": "sum", "aggregation_field": "books__pages",
                                   "group_by": "books__author__age"},
                                  format="json")
        self.assertEqual(resonse.status_code, 200)
        self.assertEqual(resonse.data, [{"books__author__age": self.author.age, "value": 600},
                                        {"books__author__age": self.author2.age, "value": 900}])

    def test_annotations(self):
        # aggregation over annotation
        response = self.client.get("/book/aggregation/", {"aggregation": "sum", "aggregation_field": "price_per_page"},
                                   format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 0.3070383333333333}])

        # group by annotation
        response = self.client.get("/book/aggregation/", {"aggregation": "avg", "aggregation_field": "price",
                                                          "group_by": "expensive"},
                                   format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data,
                         [{'expensive': 0, 'value': 10.993333333333334}, {'expensive': 1, 'value': 21.99}])



