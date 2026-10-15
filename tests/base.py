from rest_framework.test import APITestCase

from tests.testapp.models import Agent, Author, Book, Store


class FilteringAndOrderingTestCase(APITestCase):
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
