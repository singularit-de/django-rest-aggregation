import decimal

from rest_framework import serializers
from rest_framework.serializers import BaseSerializer

from .models import Author, Book, Publisher, Store


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = "__all__"


class BookSerializer(serializers.ModelSerializer):
    price_per_page = serializers.FloatField()
    expensive = serializers.BooleanField()

    class Meta:
        model = Book
        fields = "__all__"


class BookSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["name", "pages", "author"]


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = "__all__"


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = "__all__"


class CustomAggregationSerializer(BaseSerializer):
    def to_representation(self, instance):
        ret = {}
        for field in instance:
            if isinstance(instance[field], int):
                ret[field] = serializers.IntegerField(read_only=True).to_representation(instance[field])
            elif isinstance(instance[field], (float, decimal.Decimal)):
                ret[field] = serializers.DecimalField(
                    read_only=True, decimal_places=1, max_digits=10
                ).to_representation(float(instance[field]))
            else:
                ret[field] = serializers.CharField(read_only=True).to_representation(instance[field])
        return ret
