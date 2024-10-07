import datetime

from django.db import connection
from rest_framework.test import APITestCase

from tests.models import Author, Book, Store, Agent


class TestBasicFunctionality(APITestCase):
    def setUp(self):
        author = Author(name="John", age=20)
        author.save()
        Book(
            name="Book1",
            pages=100,
            price=10.50,
            rating=4.5,
            author=author,
            pubdate="2020-01-01",
        ).save()
        Book(
            name="Book2",
            pages=200,
            price=12.49,
            rating=4.0,
            author=author,
            pubdate="2020-01-02",
        ).save()
        Book(
            name="Book3",
            pages=300,
            price=19.99,
            rating=3.5,
            author=author,
            pubdate="2020-01-03",
        ).save()
        Book(
            name="Book4",
            pages=400,
            price=9.99,
            rating=3.0,
            author=author,
            pubdate="2020-01-04",
        ).save()
        Book(
            name="Book5",
            pages=500,
            price=23.99,
            rating=2.5,
            author=author,
            pubdate="2020-01-05",
        ).save()

    def test_database(self):
        print("\n--- Database ---")
        print(connection.vendor)
        if not connection.vendor == "microsoft":
            print(connection.get_database_version())
        print("----------------\n")

    def test_count(self):
        response = self.client.get("/book/aggregation/", {"aggregation": "count"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 5}])

    def test_sum(self):
        # Sum of IntegerField
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "sum", "aggregation_field": "pages"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 1500}])

        # Sum of FloatField
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "sum", "aggregation_field": "price"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 76.96000000000001}])

        # Sum of DecimalField
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "sum", "aggregation_field": "rating"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 17.5}])

    def test_avg(self):
        # Avg of IntegerField
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "avg", "aggregation_field": "pages"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 300}])

        # Avg of FloatField
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "avg", "aggregation_field": "price"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 15.392000000000001}])

        # Avg of DecimalField
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "avg", "aggregation_field": "rating"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 3.5}])

    def test_minimum(self):
        # Minimum of IntegerField
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "minimum", "aggregation_field": "pages"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 100}])

        # Minimum of FloatField
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "minimum", "aggregation_field": "price"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 9.99}])

        # Minimum of DecimalField
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "minimum", "aggregation_field": "rating"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 2.5}])

        # Minimum of DateField
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "minimum", "aggregation_field": "pubdate"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": datetime.date(2020, 1, 1)}])

    def test_maximum(self):
        # Maximum of IntegerField
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "maximum", "aggregation_field": "pages"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 500}])

        # Maximum of FloatField
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "maximum", "aggregation_field": "price"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 23.99}])

        # Maximum of DecimalField
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "maximum", "aggregation_field": "rating"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 4.5}])

        # Maximum of DateField
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "maximum", "aggregation_field": "pubdate"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": datetime.date(2020, 1, 5)}])


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
            {"aggregation": "count", "group_by": "author"},
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
            {"aggregation": "count", "group_by": "stores__name,author__name"},
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
            {"aggregation": "count", "group_by": "author__name"},
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


class TestValidation(APITestCase):
    def setUp(self):
        self.author = Author(name="John", age=20)
        self.author.save()
        Book(
            name="Book1",
            pages=100,
            price=10.55,
            rating=4.5,
            author=self.author,
            pubdate="2020-01-01",
        ).save()

    def test_aggregation_validation(self):
        response = self.client.get("/book/aggregation/", {}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "'aggregation' is required")

        response = self.client.get("/book/aggregation/", {"aggregation": "invalid"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["error"],
            "'aggregation' must be one of ['average', 'avg', 'count', 'max', 'maximum', 'min', " "'minimum', 'sum']",
        )

        response = self.client.get("/book/aggregation/", {"aggregation": ["test", 123]}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "Only one aggregation is allowed")

    def test_aggregation_field_validation(self):
        response = self.client.get("/book/aggregation/", {"aggregation": "sum"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "'aggregation_field' is required")

        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "sum", "aggregation_field": "invalid"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "'aggregation_field' is not valid")

        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "sum", "aggregation_field": ["test", 123]},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "Only one aggregation_field is allowed")

        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "sum", "aggregation_field": "name"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "'aggregation_field' must be a number field")

        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "max", "aggregation_field": "name"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["error"],
            "'aggregation_field' must be a number or a date field",
        )

    def test_group_by_validation(self):
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "count", "group_by": "invalid"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "'group_by' is not valid")

        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "count", "group_by": ["test", 123]},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "please use comma separated values for grouping")

    def test_empty_aggregated_queryset(self):
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "count", "group_by": "author__name", "value__gt": 1},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])


class TestFilteringAndOrdering(APITestCase):
    def setUp(self):
        self.agent1 = Agent(name="Adalbert Erl", address="Bookstreet 12")
        self.agent1.save()
        self.agent2 = Agent(name="Balthasar König", address="Pagepassage 98")
        self.agent2.save()
        self.author = Author(name="John", age=20, agent=self.agent1)
        self.author.save()
        self.author2 = Author(name="Jane", age=30, agent=self.agent2)
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
            rating=3.2,
            author=self.author,
            pubdate="2020-01-04",
        ).save()
        Book(
            name="Book5",
            pages=500,
            price=23.99,
            rating=3.5,
            author=self.author2,
            pubdate="2020-01-05",
        ).save()
        Book(
            name="Book6",
            pages=600,
            price=20.99,
            rating=2.0,
            author=self.author2,
            pubdate="2020-01-06",
        ).save()
        Book(
            name="Book7",
            pages=700,
            price=16.00,
            rating=4.7,
            author=self.author2,
            pubdate="2020-01-07",
        ).save()
        Book(
            name="Book8",
            pages=800,
            price=28.99,
            rating=3.9,
            author=self.author2,
            pubdate="2020-01-08",
        ).save()

        book1 = Book.objects.get(name="Book1")
        book2 = Book.objects.get(name="Book2")
        book3 = Book.objects.get(name="Book3")
        book4 = Book.objects.get(name="Book4")
        book5 = Book.objects.get(name="Book5")
        book6 = Book.objects.get(name="Book6")
        book7 = Book.objects.get(name="Book7")
        book8 = Book.objects.get(name="Book8")

        self.store = Store(name="Store1")
        self.store.save()
        self.store.books.set([book1, book3, book5, book7])

        self.store2 = Store(name="Store2")
        self.store2.save()
        self.store2.books.set([book2, book4, book6, book8])

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
                "test123__gt": 2600,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            [{"name": "Jane", "test123": 2600}, {"name": "John", "test123": 1000}],
        )

    def test_ordering_aggregation(self):
        # ordering by aggregation
        response = self.client.get(
            "/book/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "pages",
                "group_by": "author,stores",
                "ordering": "value",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            [
                {"author": self.author.pk, "stores": self.store.pk, "value": 400},
                {"author": self.author.pk, "stores": self.store2.pk, "value": 600},
                {"author": self.author2.pk, "stores": self.store.pk, "value": 1200},
                {"author": self.author2.pk, "stores": self.store2.pk, "value": 1400},
            ],
        )

        response = self.client.get(
            "/book/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "pages",
                "group_by": "author,stores",
                "ordering": "-value",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            [
                {"author": self.author2.pk, "stores": self.store2.pk, "value": 1400},
                {"author": self.author2.pk, "stores": self.store.pk, "value": 1200},
                {"author": self.author.pk, "stores": self.store2.pk, "value": 600},
                {"author": self.author.pk, "stores": self.store.pk, "value": 400},
            ],
        )

    def test_ordering(self):
        response = self.client.get(
            "/book/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "pages",
                "group_by": "author__name,stores",
                "ordering": "-author__name",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            [
                {"author__name": "John", "stores": self.store.pk, "value": 400},
                {"author__name": "John", "stores": self.store2.pk, "value": 600},
                {"author__name": "Jane", "stores": self.store.pk, "value": 1200},
                {"author__name": "Jane", "stores": self.store2.pk, "value": 1400},
            ],
        )

    def test_ordering_by_multiple_fields(self):
        response = self.client.get(
            "/book/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "pages",
                "group_by": "author__name,stores",
                "ordering": "author__name,value",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            [
                {"author__name": "Jane", "stores": self.store.pk, "value": 1200},
                {"author__name": "Jane", "stores": self.store2.pk, "value": 1400},
                {"author__name": "John", "stores": self.store.pk, "value": 400},
                {"author__name": "John", "stores": self.store2.pk, "value": 600},
            ],
        )

        response = self.client.get(
            "/book/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "pages",
                "group_by": "author__name,stores",
                "ordering": "author__name,-value",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            [
                {"author__name": "Jane", "stores": self.store2.pk, "value": 1400},
                {"author__name": "Jane", "stores": self.store.pk, "value": 1200},
                {"author__name": "John", "stores": self.store2.pk, "value": 600},
                {"author__name": "John", "stores": self.store.pk, "value": 400},
            ],
        )

    def test_multi_relation_ordering(self):
        response = self.client.get(
            "/book/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "pages",
                "group_by": "author__name,stores",
                "ordering": "author__agent__name",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            [
                {"author__name": "John", "stores": self.store.pk, "value": 400},
                {"author__name": "John", "stores": self.store2.pk, "value": 600},
                {"author__name": "Jane", "stores": self.store.pk, "value": 1200},
                {"author__name": "Jane", "stores": self.store2.pk, "value": 1400},
            ],
        )


class TestCustomization(APITestCase):
    def setUp(self):
        self.author = Author(name="John", age=20)
        self.author.save()
        Book(
            name="Book1",
            pages=100,
            price=10.55,
            rating=4.5,
            author=self.author,
            pubdate="2020-01-01",
        ).save()

    def test_custom_serializer_and_name(self):
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "sum", "aggregation_field": "price"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 10.55}])

        response = self.client.get(
            "/customized_book/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "price",
                "ordering": "CustomizedValue",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"], [{"group": "all", "CustomizedValue": "10.6"}])

    def test_pagination(self):
        response = self.client.get(
            "/customized_book/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "price",
                "ordering": "CustomizedValue",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.keys(), {"count", "next", "previous", "results"})

    def test_ordering_all_field(self):
        response = self.client.get(
            "/customized_book/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "price",
                "CustomizedValue__gte": 20,
                "ordering": "CustomizedValue",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"], [])

    def test_pagination_count(self):
        response = self.client.get(
            "/customized_book/aggregation/",
            {
                "aggregation": "sum",
                "aggregation_field": "price",
                "ordering": "CustomizedValue",
                "CustomizedValue__lte": 0,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)