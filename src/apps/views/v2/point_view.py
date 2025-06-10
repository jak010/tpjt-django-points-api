from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from src.apps.service.v2.point_service import PointRedisService
from src.apps.views.schema import (
    point_earn_schema
)


class PointEarnView(APIView):
    point_service = PointRedisService()

    @extend_schema(
        tags=["V2-POINT"],
        operation_id="V1-POINT_EARN",
        description="포인트 적립하기",
        request=point_earn_schema.PointEarnRequest,
        responses={
            200: point_earn_schema.PointEarnResponse
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = point_earn_schema.PointEarnRequest(data=request.data)
        serializer.is_valid(raise_exception=True)

        response = point_earn_schema.PointEarnResponse(
            {
                "data": self.point_service.earn_point(
                    user_id=serializer.validated_data["user_id"],
                    amount=serializer.validated_data["amount"],
                    description=serializer.validated_data["description"],
                )
            }
        )

        return Response(content_type="application/json", status=200, data=response.data)
