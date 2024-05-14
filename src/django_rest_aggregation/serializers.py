from rest_framework import serializers


class PassTroughField(serializers.Field):

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        return data


class AggregationSerializer(serializers.Serializer):
    """
    Serializer for aggregation requests.
    Authored by Tim Streicher
    """

    value = serializers.SerializerMethodField(method_name='serialize_value')

    def serialize_value(self, obj):
        return obj['value']

    def __init__(self, *args, **kwargs):
        # Instantiate the superclass normally
        super(AggregationSerializer, self).__init__(*args, **kwargs)

        fields = self.context['request'].query_params.get('group_by')
        allowed = {self.context['name']}
        if fields:
            fields = fields.split(',')
            allowed.update(fields)
        else:
            allowed.add('group')

        # Drop any fields that are not specified in the `fields` argument except value.
        existing = set(self.fields.keys())
        for field_name in existing - allowed:
            self.fields.pop(field_name)

        for field_name in allowed:
            field = self.fields.get(field_name)
            # add field for unknown field_names
            if field is None:
                self.fields[field_name] = PassTroughField()
