from rest_framework import serializers

from src.apps.models import Point


class PointEarnRequest(serializers.Serializer):
    """ 포인트 적립하기 """
    user_id = serializers.IntegerField()
    amount = serializers.IntegerField()
    description = serializers.CharField(max_length=255)


class PointEarnResponse(serializers.Serializer):
    """ 포인트 적립하기 """

    class _PointEarnModelSerializer(serializers.ModelSerializer):
        class Meta:
            model = Point
            fields = ["id", "user_id", "amount", "type", "description", "balance_snapshot"]

    data = _PointEarnModelSerializer()
