import decimal

from rest_framework import serializers
from rest_framework.serializers import BaseSerializer


class AggregationSerializer(BaseSerializer):
    def to_representation(self, instance):
        ret = {}
        for field in instance.keys():
            if isinstance(instance[field], int):
                ret[field] = serializers.IntegerField(read_only=True).to_representation(instance[field])
            elif isinstance(instance[field], float) or isinstance(instance[field], decimal.Decimal):
                ret[field] = serializers.FloatField(read_only=True).to_representation(float(instance[field]))
            else:
                ret[field] = serializers.CharField(read_only=True).to_representation(instance[field])
        return ret
