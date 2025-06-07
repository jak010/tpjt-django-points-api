from rest_framework.views import APIView
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from src.apps.service.v1.point_service import PointService
from src.apps.views.v1.schema.point_earn_schema import PotinEarnSchema


class PointEarnView(APIView):
    point_service = PointService()

    @extend_schema(
        tags=["V1-POINT"],
        operation_id="V1-POINT_EARN",
        description="포인트 적립하기",
        request=PotinEarnSchema.PointEarnRequest,
        responses={
            200: PotinEarnSchema.PointEarnResponse
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = PotinEarnSchema.PointEarnRequest(data=request.data)
        serializer.is_valid(raise_exception=True)

        response = PotinEarnSchema.PointEarnResponse(
            {
                "data": self.point_service.earn_points(
                    user_id=serializer.validated_data["user_id"],
                    amount=serializer.validated_data["amount"],
                    description=serializer.validated_data["description"],
                )
            }
        )

        return Response(content_type="application/json", status=200, data=response.data)
