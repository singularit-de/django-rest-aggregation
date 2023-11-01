from rest_framework import serializers

from .models import Author, Book, Store


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    price_per_page = serializers.FloatField()
    expensive = serializers.BooleanField()

    class Meta:
        model = Book
        fields = '__all__'


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'
