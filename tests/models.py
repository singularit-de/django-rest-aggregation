from django.db import models


class Agent(models.Model):
    name = models.CharField(max_length=300)
    address = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    agent =models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    name = models.CharField(max_length=300)
    pages = models.IntegerField()
    price = models.FloatField()
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books")
    pubdate = models.DateField()

    def __str__(self):
        return self.name


class Store(models.Model):
    name = models.CharField(max_length=300)
    books = models.ManyToManyField(Book, related_name="stores")

    def __str__(self):
        return self.name
