from rest_framework import serializers

from src.apps.models import Point, PointBalance


class PointHistoryResponse(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = '__all__'
