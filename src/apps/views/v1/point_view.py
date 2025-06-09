from drf_spectacular.utils import extend_schema
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from src.apps.service.v1.point_service import PointService
from src.apps.views.v1.schema import (
    point_earn_schema,
    point_use_schema,
    point_cancel_schema,
    point_search_schema
)


class PointHistoryView(APIView, LimitOffsetPagination):
    point_service = PointService()

    @extend_schema(
        tags=["V1-POINT"],
        operation_id="V1-POINT-SEARCH",
        description="포인트 조회하기",
        parameters=[point_search_schema.PointHistoryRequest],
        responses={
            200: point_search_schema.PointHistoryPaginateResponse()
        }
    )
    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')

        request_serializer = point_search_schema.PointHistoryRequest(data=request.query_params)
        request_serializer.is_valid(raise_exception=True)

        paginate_queryset = self.paginate_queryset(
            self.point_service.search_points(user_id=user_id),
            request,
            view=self
        )

        paginate = point_search_schema.PointHistoryPaginateResponse(
            {
                "count": self.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "data": paginate_queryset
            }
        )

        return Response(
            content_type="application/json",
            status=200,
            data=paginate.data
        )


class PointEarnView(APIView):
    point_service = PointService()

    @extend_schema(
        tags=["V1-POINT"],
        operation_id="V1-POINT_EARN",
        description="포인트 적립하기",
        request=point_earn_schema.PointEarnRequest,
        responses={
            200: point_earn_schema.PointEarnResponse
        }
    )
    def post(self, request, *args, **kwargs):
        from django.db import connection, reset_queries
        serializer = point_earn_schema.PointEarnRequest(data=request.data)
        serializer.is_valid(raise_exception=True)

        response = point_earn_schema.PointEarnResponse(
            {
                "data": self.point_service.earn_points(
                    user_id=serializer.validated_data["user_id"],
                    amount=serializer.validated_data["amount"],
                    description=serializer.validated_data["description"],
                )
            }
        )

        return Response(content_type="application/json", status=200, data=response.data)


class PointUseView(APIView):
    point_service = PointService()

    @extend_schema(
        tags=["V1-POINT"],
        operation_id="V1-POINT_USE",
        description="포인트 사용하기",
        request=point_use_schema.PointUseRequest,
        responses={
            200: point_use_schema.PointUseResponse
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = point_use_schema.PointUseRequest(data=request.data)
        serializer.is_valid(raise_exception=True)

        response = point_use_schema.PointUseResponse(
            {
                "data": self.point_service.use_points(
                    user_id=serializer.validated_data["user_id"],
                    amount=serializer.validated_data["amount"],
                    description=serializer.validated_data["description"],
                )
            }
        )

        return Response(content_type="application/json", status=200, data=response.data)


class PointCancelView(APIView):
    point_service = PointService()

    @extend_schema(
        tags=["V1-POINT"],
        operation_id="V1-POINT_CANCEL",
        description="포인트 취소하기",
        request=point_cancel_schema.PointCancelRequest,
        responses={
            200: point_cancel_schema.PointCancelResponse
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = point_cancel_schema.PointCancelRequest(data=request.data)
        serializer.is_valid(raise_exception=True)

        response = point_cancel_schema.PointCancelResponse(
            {
                "data": self.point_service.cancel_points(
                    point_id=kwargs.get("point_id"),
                    user_id=serializer.validated_data["user_id"],
                    amount=serializer.validated_data["amount"],
                    description=serializer.validated_data["description"],
                )
            }
        )

        return Response(content_type="application/json", status=200, data=response.data)
