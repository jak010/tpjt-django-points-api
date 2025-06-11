import redis
from django.core.cache import cache
from django.db import transaction

from src.apps.models import PointBalance, Point


class PointRedisService:
    POINT_BALANCE_MAP = 'point:balance'  # 포인트 잔액 저장 키값
    POINT_LOCK_PREFIX = "point:lock:"
    LOCK_WAIT_TIME = 3
    LOCK_LEASE_TIME = 3

    def get_balance(self, user_id: int):
        """ 포인트 잔액 조회

        Implements
            캐시에서 잔액 조회 -> 캐시 없으면 DB에서 조회 후 캐시 업데이트


        """
        cached_balance = self.get_balance_from_cache(user_id=user_id)
        if cached_balance is None:
            cached_balance = self.get_balance_from_db(user_id=user_id)
            self.update_balance_cache(user_id, cached_balance)

        return cached_balance

    @transaction.atomic
    def earn_point(self, user_id: int, amount: float, description: str):
        """ Redis 기반 포인트 적립 처리

        Implements
            분산 락 획득 -> 캐시된 잔액 조회 (없으면 DB에서 조회) -> 포인트 잔액 증가 -> DB 저장 및 캐시 업데이트 -> 포인트 인력 저장

        TODO
            - 25.06.11 : 락의 범위가 크기 때문에 줄이는 방향 고민하기

        """

        try:
            with cache.lock(
                    f"{self.POINT_LOCK_PREFIX}{user_id}",
                    timeout=self.LOCK_LEASE_TIME,
                    blocking_timeout=self.LOCK_WAIT_TIME
            ) as lock:  # 분산 락 획득

                # 캐시된 잔액 조회
                current_balance = self.get_balance_from_cache(user_id)
                if current_balance is None:
                    # 캐시된 잔액이 없으면 DB에서 조회
                    current_balance = self.get_balance_from_db(user_id)

                    #  캐시 업데이트
                    self.update_balance_cache(user_id, current_balance)

                # 포인트 잔액 증가

                point_balance, _created = PointBalance.objects.get_or_create(user_id=user_id, defaults={"balance": 0})
                point_balance.add_balance(amount=amount)
                point_balance.save()

                self.update_balance_cache(point_balance.user_id, point_balance.balance)

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
        except redis.exceptions.LockError as e:
            raise Exception("Too Many Connection Issue Requests")  # Lock을 잡지 못 헀으니 다시 시도해달라고 요청하기 ?

    def use_point(self, user_id: int, amount: float, description: str):
        """ 포인트 사용하기

        Implements
            - 분산 락 획득 -> 캐시된 잔액 조회(없으면 DB에서 조회) -> 잔액 체크 -> 포인트 잔액 감소 -> DB 저장 및 캐시 업데이트 -> 포인트 이력 저장

        """
        try:
            with cache.lock(
                    f"{self.POINT_LOCK_PREFIX}{user_id}",
                    timeout=self.LOCK_LEASE_TIME,
                    blocking_timeout=self.LOCK_WAIT_TIME
            ) as lock:

                current_balance = self.get_balance_from_cache(user_id=user_id)

                if current_balance is None:
                    current_balance = self.get_balance_from_db(user_id=user_id)
                    self.update_balance_cache(user_id, current_balance)

                if current_balance < amount:
                    raise Exception("사용자의 포인트 재고은 취소된 포인트보다 작음")

                point_balance = PointBalance.objects.filter(user_id=user_id).first()
                if point_balance is None:
                    raise Exception("사용자를 찾을 수 없음")

                point_balance.subtract_balance(amount)
                self.update_balance_cache(user_id, point_balance.balance)

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

        except redis.exceptions.LockError as e:
            raise Exception("Too Many Connection Issue Requests")

    def cancel_point(self, point_id: int, description: str):
        """ 포인트 취소 처리

        Implements
        ---
            - 원본 포인트 이력 조회 -> 분산 락 획득 -> 취소 가능 여부 확인 -> 포인트 잔액 원복(적립 취소는 차감, 사용 취소는 증가)
                -> DB 저장 및 캐시 업데이트 -> 취소 이력 저장

        """

        save_point = Point.object.filter(id=point_id).first()
        if save_point is None:
            raise Exception("Point Not Found")

        try:
            with cache.lock(
                    f"{self.POINT_LOCK_PREFIX}{save_point.user_id}",
                    timeout=self.LOCK_LEASE_TIME,
                    blocking_timeout=self.LOCK_WAIT_TIME
            ) as lock:

                # 캐시된 잔액 조회
                current_balance = self.get_balance_from_cache(save_point.user_id)
                if current_balance is None:
                    # 캐시된 잔액이 없면 DB에서 조회
                    current_balance = self.get_balance_from_db(save_point.user_id)

                    #  캐시 업데이트
                    self.update_balance_cache(save_point.user_id, current_balance)

                # 포인트 잔액 증가
                point_balance = PointBalance.objects.filter(user_id=save_point.user_id).first()
                if point_balance is None:
                    raise Exception("사용자를 찾을 수 없음")

                if save_point.type == Point.Type.EARN:
                    if current_balance < save_point.amount:
                        raise Exception("사용자의 포인트 재고은 취소된 포인트보다 작음")

                    new_balance = current_balance - save_point.amount
                elif save_point.type == Point.Type.USED:
                    new_balance = current_balance + save_point.amount
                else:
                    raise Exception("invalid point type")

                point_balance.set_balance(new_balance)
                point_balance.save()

                # 취소 이력 저장
                point = Point.initilaized(
                    user_id=save_point.user_id,
                    amount=save_point.amount,
                    type=Point.Type.CANCELED,
                    description=description,
                    balance_snapshot=point_balance.balance,
                    point_balance=point_balance
                )
                point.save()
                return point

        except redis.exceptions.LockError as e:
            raise Exception("Too Many Connection Issue Requests")

    def get_balance_from_db(self, user_id):
        point_balance = PointBalance.objects.filter(user_id=user_id).first()
        return point_balance.balance

    def get_balance_from_cache(self, user_id) -> int:
        """ Redis 기반 포인트 잔액 조회

        Implements
            Argument로 입력받은 값들 캐시에서 읽기

        Note
            FastCampus 강의에서는 단순히 ORM으로 읽은 값을 조회해서 반환한다.

        """
        balance_map = cache.get(f"{self.POINT_BALANCE_MAP}")
        if balance_map is not None:
            return balance_map.get(user_id)

    def update_balance_cache(self, user_id, current_balance):
        """ Redis 기반 포인트 잔액 업데이트

        Implements
            Argument로 입력받은 값들 캐시에 저장하기

        """
        return cache.set(f"{self.POINT_BALANCE_MAP}:{user_id}", current_balance)
