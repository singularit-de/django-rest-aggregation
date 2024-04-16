import decimal

from rest_framework import serializers
from rest_framework.serializers import BaseSerializer


class CustomAggregationSerializer(BaseSerializer):
    def to_representation(self, instance):
        ret = {}
        for field in instance.keys():
            if isinstance(instance[field], int):
                ret[field] = serializers.IntegerField(read_only=True).to_representation(instance[field])
            elif isinstance(instance[field], float) or isinstance(instance[field], decimal.Decimal):
                ret[field] = serializers.DecimalField(
                    read_only=True, decimal_places=1, max_digits=10
                ).to_representation(float(instance[field]))
            else:
                ret[field] = serializers.CharField(read_only=True).to_representation(instance[field])
        return ret
