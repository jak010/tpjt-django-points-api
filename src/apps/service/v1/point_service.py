from src.apps.models import Point
from src.apps.models.point_balance import PointBalance

from django.db import transaction


class PointService:

    @transaction.atomic()
    def earn_points(self, user_id: int, amount: float, description: str) -> Point:
        """ 포인트 적립하기



        """

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

    def use_points(self, user_id: int, amount: float, description: str):
        """ 포인트 사용하기 """
        ...

    def cancel_points(self, user_id: int, amount: float, description: str):
        """ 포인트 취소하기 """
        ...

    def get_balance(self, user_id: int):
        """ 포인트 재고조회하기 """
        ...

    def get_point_history(self, user_id: int):
        """ 포인트 재고조회하기 """
        ...
