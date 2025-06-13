import backoff
from django.db import transaction, IntegrityError
from rest_framework.exceptions import NotFound

from src.apps.models import Point
from src.apps.models.point_balance import PointBalance

from src.apps.service.exceptions import OptimisticLockingError

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def log_backoff(details):
    """ backoff hook

    Implements:
        backoff.on_exception 데코레이터가 적용된 경우 실행하는 함수

    Note
        이 함수를 통해 재시도가 처리될 때 로깅이 가능하도록 만들 수 있음

    TODO
        25-06-10, 이 함수가 호출된 시점에 재시도된 횟수를 DB에 기록하는 용도로 개선 가능할듯

    """
    logger.warning(
        "Retrying %s in %.1f seconds after %d tries due to %s",
        details['target'].__name__,
        details['wait'],
        details['tries'],
        details['exception']
    )


class PointService:

    # @backoff.on_exception(backoff.expo, exception=OptimisticLockingError, max_time=2, max_tries=10, on_backoff=log_backoff)
    # @backoff.on_exception(backoff.expo, exception=IntegrityError, max_time=2, max_tries=10)
    @transaction.atomic
    def earn_points(self, user_id: int, amount: float, description: str) -> Point:
        """ 포인트 적립하기
        Implements:
            이미 존재하는 사용자라면 amount 만큼 더해주고, 존재하지 않는 경우 balance 0으로 초기화

        Args:
            user_id (int): 사용자 ID
            amount (float): 포인트 적립한 금액
            description (str): 포인트 적립 설명

        Note:
            - 강의에서 로직을 그대로 따라 작성했는데 포인트 적립은 입력한 amount 만큼 upsert를 처리하는게 맞을 듯
            - Django 에서 Isolation level 다루기
              - https://medium.com/buserbrasil/database-isolation-levels-anomalies-and-how-to-handle-them-with-django-992889d233d5

        TODO:
            - 25-06-10, REPEATABLE_READ와 Point Balance.filter의 경우 Optmistic Lock 처리하기
                Ref, https://github.com/dobby-teacher/fastcampus-promotion-project/blob/e57cae3c09264215203c00f51896e4e28249071e/PROJECT-PROMOTION/promotion/point-service/src/main/java/com/fastcampus/pointservice/repository/PointBalanceRepository.java#L11
        """

        point_balance: PointBalance = PointBalance.objects \
            .filter(user_id=user_id) \
            .first()

        if point_balance is None:
            point_balance = PointBalance.initialized(user_id=user_id, balance=amount)
            point_balance.save()  # IntegrityError
        else:
            point_balance = point_balance.add_balance(amount)
            point_balance = point_balance.update_with_optimistic_lock()  # OptimisticLockingError

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
        """ 포인트 사용하기
        Implements
            사용자 포인트를 찾고, 사용한 금액만큼 차감처리해주기

        Args:
            user_id (int): 사용자 ID
            amount (float): 포인트 사용한 금액
            description (str): 포인트 사용 설명

        Notes:
            FastCampus 강의에서는 이 함수에도 REPEATABLE_READ 수준으로 락을 걸어준다.

        TODO:
         - 2025-06-10

        """

        point_balance: PointBalance = PointBalance.objects.filter(user_id=user_id).first()
        if point_balance is None:
            raise NotFound()

        point_balance.subtract_balance(amount)

        point = Point.initilaized(
            user_id=user_id,
            amount=amount,
            type=Point.Type.USED,
            description=description,
            balance_snapshot=point_balance.balance,
            point_balance=point_balance
        )

        point_balance.save()
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
        return PointBalance.objects.filter(user_id=user_id).first()

    def get_point_history(self, user_id: int):
        """ 포인트 적립 내역 조회하기
        Implements
            Point 모델을 기준으로 페이지네이션 리턴하기
        Note
            FastCampus 강의에서는 PointBalances 모델과의 관계를 설정해서 가져온다.

        """
        if user_id is None:
            raise NotFound()

        return Point.objects.filter(user_id=user_id)
