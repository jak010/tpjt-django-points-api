from rest_framework import serializers

from src.apps.models import Point


class PointCancelRequest(serializers.Serializer):
    user_id = serializers.IntegerField()
    amount = serializers.IntegerField()
    description = serializers.CharField(max_length=255)


class PointCancelResponse(serializers.Serializer):
    class _PointCancelModelSerializer(serializers.ModelSerializer):
        class Meta:
            model = Point
            fields = ["id", "user_id", "amount", "type", "description", "balance_snapshot", "created_at"]

    data = _PointCancelModelSerializer()
