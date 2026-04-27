from rest_framework import serializers

class RouteMetaSerializer(serializers.Serializer):
    title = serializers.CharField()
    icon = serializers.CharField(required=False, allow_blank=True)


class AsyncRouteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    parent = serializers.IntegerField(default=0)
    path = serializers.CharField()
    component = serializers.CharField()
    meta = RouteMetaSerializer()