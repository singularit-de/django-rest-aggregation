from rest_framework.test import APITestCase

from tests.testapp.models import Agent, Author, Book, Store


class TestSecurity(APITestCase):
    def setUp(self):
        agent = Agent.objects.create(name="Agent", address="Secret Street 1")
        self.john = Author.objects.create(name="John", age=20, agent=agent)
        self.jane = Author.objects.create(name="Jane", age=30)
        Book.objects.create(name="B", pages=100, price=10, rating=4, author=self.john, pubdate="2020-01-01")
        Book.objects.create(name="A", pages=200, price=20, rating=3, author=self.john, pubdate="2020-01-02")
        Book.objects.create(name="C", pages=300, price=30, rating=2, author=self.jane, pubdate="2020-01-03")

    def test_group_by_outside_allowlist_is_rejected(self):
        # the book API does not expose agents
        response = self.client.get(
            "/book/aggregation/", {"aggregation": "count", "group_by": "author__agent__address"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "'group_by' is not valid")

    def test_aggregation_field_outside_allowlist_is_rejected(self):
        # the book API does not expose author__age
        response = self.client.get(
            "/book/aggregation/", {"aggregation": "max", "aggregation_field": "author__age"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "'aggregation_field' is not valid")

    def test_default_allowlist_is_the_serializer_fields(self):
        # customized_book sets no aggregation_fields; BookSerializer exposes author, not author__name
        response = self.client.get(
            "/customized_book/aggregation/", {"aggregation": "count", "group_by": "author"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(
            "/customized_book/aggregation/", {"aggregation": "count", "group_by": "author__name"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "'group_by' is not valid")

    def test_ordering_by_non_grouped_field_keeps_grouping(self):
        # "name" is not a result column and is ignored, both in the view's OrderingFilter and after the aggregation
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "count", "group_by": "author", "ordering": "name,author"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            [{"author": self.john.pk, "value": 2}, {"author": self.jane.pk, "value": 1}],
        )

    def test_unknown_ordering_field_is_ignored(self):
        # unknown term: 200, not 500
        response = self.client.get(
            "/book/aggregation/",
            {"aggregation": "count", "group_by": "author", "ordering": "doesnotexist,author"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            [{"author": self.john.pk, "value": 2}, {"author": self.jane.pk, "value": 1}],
        )

    def test_group_by_field_limit(self):
        # at most 3 group_by fields by default
        response = self.client.get(
            "/book/aggregation/", {"aggregation": "count", "group_by": "name,pages,price,rating"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "'group_by' accepts at most 3 fields")


class TestAggregationModels(APITestCase):
    """models_book: serializer exposes name, pages, author; aggregation_models = [Author, "testapp.Store"]."""

    def setUp(self):
        agent = Agent.objects.create(name="Agent", address="Secret Street 1")
        self.john = Author.objects.create(name="John", age=20, agent=agent)
        self.jane = Author.objects.create(name="Jane", age=30)
        b1 = Book.objects.create(name="B", pages=100, price=10, rating=4, author=self.john, pubdate="2020-01-01")
        b2 = Book.objects.create(name="A", pages=200, price=20, rating=3, author=self.john, pubdate="2020-01-02")
        b3 = Book.objects.create(name="C", pages=300, price=30, rating=2, author=self.jane, pubdate="2020-01-03")
        Store.objects.create(name="North").books.set([b1, b2, b3])
        Store.objects.create(name="South").books.set([b3])

    def get(self, params):
        return self.client.get("/models_book/aggregation/", params, format="json")

    def test_listed_model_field_is_allowed(self):
        response = self.get(
            {"aggregation": "sum", "aggregation_field": "pages", "group_by": "author__name", "ordering": "author__name"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data, [{"author__name": "Jane", "value": 300}, {"author__name": "John", "value": 300}]
        )

    def test_listed_model_aggregation_field_is_allowed(self):
        response = self.get({"aggregation": "max", "aggregation_field": "author__age"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"group": "all", "value": 30}])

    def test_model_given_as_string_is_allowed(self):
        response = self.get({"aggregation": "count", "group_by": "stores__name", "ordering": "stores__name"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"stores__name": "North", "value": 3}, {"stores__name": "South", "value": 1}])

    def test_serializer_fields_of_base_model_stay_allowed(self):
        response = self.get({"aggregation": "count", "group_by": "author", "ordering": "author"})
        self.assertEqual(response.status_code, 200)

    def test_base_model_field_outside_serializer_is_rejected(self):
        # Book itself is not in aggregation_models
        response = self.get({"aggregation": "sum", "aggregation_field": "price"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "'aggregation_field' is not valid")

    def test_unlisted_model_on_path_is_rejected(self):
        # Author is listed, Agent is not
        response = self.get({"aggregation": "count", "group_by": "author__agent__address"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "'group_by' is not valid")

    def test_path_back_to_base_model_is_rejected(self):
        # would bypass the serializer allowlist of Book
        for path in ["stores__books__price", "author__books__price"]:
            response = self.get({"aggregation": "sum", "aggregation_field": path})
            self.assertEqual(response.status_code, 400, path)
            self.assertEqual(response.data["error"], "'aggregation_field' is not valid")

    def test_unknown_field_on_listed_model_is_rejected(self):
        response = self.get({"aggregation": "count", "group_by": "author__doesnotexist"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "'group_by' is not valid")
