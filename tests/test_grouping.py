from rest_framework.test import APITestCase

from tests.testapp.models import Author, Book, Store


class TestGroupingAndAnnotations(APITestCase):
    def setUp(self):
        self.author = Author(name="John", age=20)
        self.author.save()
        self.author2 = Author(name="Jane", age=30)
        self.author2.save()

        Book(
            name="Book1",
            pages=100,
            price=10.50,
            rating=4.5,
            author=self.author,
            pubdate="2020-01-01",
        ).save()
        Book(
            name="Book2",
            pages=200,
            price=12.49,
            rating=4.0,
            author=self.author,
            pubdate="2020-01-02",
        ).save()
        Book(
            name="Book3",
            pages=300,
            price=19.99,
            rating=3.5,
            author=self.author,
            pubdate="2020-01-03",
        ).save()
        Book(
            name="Book4",
            pages=400,
            price=09.99,
            rating=3.0,
            author=self.author2,
            pubdate="2020-01-04",
        ).save()
        Book(
            name="Book5",
            pages=500,
            price=23.99,
            rating=2.5,
            author=self.author2,
            pubdate="2020-01-05",
        ).save()

        book1 = Book.objects.get(name="Book1")
        book3 = Book.objects.get(name="Book3")
        book5 = Book.objects.get(name="Book5")

        book2 = Book.objects.get(name="Book2")
        book4 = Book.objects.get(name="Book4")

        store = Store(name="Store1")
        store.save()
        store.books.set([book1, book3, book5])

        store = Store(name="Store2")
        store.save()
        store.books.set([book2, book4])

    def test_group_by(self):
        # Simple Group by
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "count", "group_by": "author", "ordering": "author"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            [
                {"author": self.author.pk, "value": 3},
                {"author": self.author2.pk, "value": 2},
            ],
        )

        # Groupy by multiple fields
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "count", "group_by": "stores__name,author__name", "ordering": "stores__name,author__name"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        (
            self.assertEqual(
                response.data,
                [
                    {"stores__name": "Store1", "author__name": "Jane", "value": 1},
                    {"stores__name": "Store1", "author__name": "John", "value": 2},
                    {"stores__name": "Store2", "author__name": "Jane", "value": 1},
                    {"stores__name": "Store2", "author__name": "John", "value": 1},
                ],
            ),
        )

    def test_group_by_related_field(self):
        # Group by foreign key related field
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "count", "group_by": "author__name", "ordering": "author__name"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            [
                {"author__name": self.author2.name, "value": 2},
                {"author__name": self.author.name, "value": 3},
            ],
        )

        # Group by many to many related field
        response = self.client.get(
            "/store/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "books__pages",
                "group_by": "books__author__age",
                "ordering": "books__author__age",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            [
                {"books__author__age": self.author.age, "value": 600},
                {"books__author__age": self.author2.age, "value": 900},
            ],
        )

    def test_annotations(self):
        # aggregation over annotation
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "sum", "aggregation_field": "price_per_page"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 0.3070383333333333}])

        # group by annotation
        response = self.client.get(
            "/book/aggregation/",
            {
                "aggregation": "avg",
                "aggregation_field": "price",
                "group_by": "expensive",
                "ordering": "expensive",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            [
                {"expensive": "expensive", "value": 21.99},
                {"expensive": "not expensive", "value": 10.993333333333334},
            ],
        )
