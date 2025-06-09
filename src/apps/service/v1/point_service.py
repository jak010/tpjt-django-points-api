from rest_framework.pagination import LimitOffsetPagination

from src.apps.models import Point, PointBalance
from src.apps.models.point_balance import PointBalance

from django.db import transaction


class PointService:

    def search_points(self, *, user_id: int):
        """ 포인트 조회하기 """

        return Point.objects.filter(user_id=user_id)

    @transaction.atomic()
    def earn_points(self, user_id: int, amount: float, description: str) -> Point:
        """ 포인트 적립하기 """

        point_balance = PointBalance.objects.filter(user_id=user_id).first()

        if point_balance is None:
            point_balance = PointBalance.initialized(
                user_id=user_id,
                balance=0,
            )
        else:
            point_balance.add_balance(amount)

        point_balance.save()

        new_point = Point.initilaized(
            user_id=user_id,
            amount=amount,
            type=Point.Type.EARN,
            description=description,
            balance_snapshot=point_balance.balance,
            point_balance=point_balance
        )
        new_point.save()
        return new_point

    @transaction.atomic()
    def use_points(self, user_id: int, amount: float, description: str):
        """ 포인트 사용하기 """

        point_balance: PointBalance = PointBalance.objects.filter(user_id=user_id).first()
        if point_balance is None:
            raise Exception("사용자를 찾을 수 없음")

        point_balance.subtract_balance(amount)
        point_balance.save()

        point = Point.initilaized(
            user_id=user_id,
            amount=amount,
            type=Point.Type.USED,
            description=description,
            balance_snapshot=point_balance.balance,
            point_balance=point_balance
        )
        point.save()

        return point

    @transaction.atomic()
    def cancel_points(self, point_id: int, user_id: int, amount: float, description: str):
        """ 포인트 취소하기 """

        original_point: Point = Point.objects.filter(id=point_id).first()
        if original_point is None:
            raise Exception("Point Not Found")
        if original_point.type == Point.Type.CANCELED:
            raise Exception("이미 취소된 포인트입니다")

        # 포인트 잔고 조회
        point_balance: PointBalance = PointBalance.objects.filter(user_id=user_id).first()
        if point_balance is None:
            raise Exception("사용자를 찾을 수 없음")

        current_balance = point_balance.balance

        if original_point.type == Point.Type.EARN.value:
            if current_balance < original_point.amount:
                raise Exception("사용자의 포인트 재고은 취소된 포인트보다 작음")

            new_balance = current_balance - original_point.amount
        elif original_point.type == Point.Type.USED.value:
            new_balance = current_balance + original_point.amount
        else:
            raise Exception("invalid point type")

        point_balance.set_balance(new_balance)
        point_balance.save()

        point = Point.initilaized(
            user_id=user_id,
            amount=amount,
            type=Point.Type.CANCELED,
            description=description,
            balance_snapshot=point_balance.balance,
            point_balance=point_balance
        )
        point.save()

        return point

    def get_balance(self, user_id: int):
        """ 포인트 재고조회하기 """
        ...

    def get_point_history(self, user_id: int):
        """ 포인트 재고조회하기 """
        ...
