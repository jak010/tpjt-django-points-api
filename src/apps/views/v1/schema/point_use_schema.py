from rest_framework import serializers

from src.apps.models import Point


class PointUseRequest(serializers.Serializer):
    """ 적립금 사용하기

    Request Examples
    {
        "user_id": 100,
        "amount": 3000,
        "description": "상품 구매 결제"
    }

    """
    user_id = serializers.IntegerField()
    amount = serializers.IntegerField()
    description = serializers.CharField(max_length=255)


class PointUseResponse(serializers.Serializer):
    """ Response, 적립금 사용하기

    Response Examples
    {
        "data": {
            "id": 1,
            "user_id": 100,
            "amount": 3000,
            "type": "USED",
            "description": "상품 구매 결제",
            "balance_snapshot": 7000,
            "created_at": "2022-01-01T00:00:00.000Z"
        }
    }

    """

    class _PointUserModelSerializer(serializers.ModelSerializer):
        class Meta:
            model = Point
            fields = ["id", "user_id", "amount", "type", "description", "balance_snapshot", "created_at"]

    data = _PointUserModelSerializer()
