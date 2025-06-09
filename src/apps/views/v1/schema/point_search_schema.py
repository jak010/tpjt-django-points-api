from rest_framework import serializers

from src.apps.models import Point, PointBalance


class PointHistoryRequest(serializers.Serializer):
    limit = serializers.IntegerField(required=False, default=10)
    offset = serializers.IntegerField(required=False, default=0)


class PointHistoryPaginateResponse(serializers.Serializer):
    class _PointSerializer(serializers.ModelSerializer):
        class Meta:
            model = Point
            fields = '__all__'

    count = serializers.IntegerField()
    next = serializers.URLField()
    previous = serializers.URLField()
    data = _PointSerializer(many=True)
