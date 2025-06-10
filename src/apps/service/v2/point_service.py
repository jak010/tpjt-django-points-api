import redis
from django.core.cache import cache

from src.apps.models import PointBalance, Point


class PointRedisService:
    POINT_BALANCE_MAP = 'point:balance'  # 포인트 잔액 저장 키값
    POINT_LOCK_PREFIX = "point:lock:"
    LOCK_WAIT_TIME = 3
    LOCK_LEASE_TIME = 3

    def earn_point(self, user_id: int, amount: float, description: str):
        """ Redis 기반 포인트 적립 처리

        Implements
            분산 락 획득 -> 캐시된 잔액 조회 (없으면 DB에서 조회) -> 포인트 잔액 증가 -> DB 저장 및 캐시 업데이트 -> 포인트 인력 저장

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
                    self.get_balance_from_db(user_id)

                    #  캐시 업데이트
                    self.update_balance_cache(user_id, current_balance)

                # 포인트 잔액 증가

                point_balance = PointBalance.objects.get_or_create(user_id=user_id, defaults={"balance": 0})
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
            print(e)
            raise Exception("Too Many Connection Issue Requests")

    # def use_point(self):
    #     ...
    #
    # def cancel_point(self):
    #     ...

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
        return balance_map.get(user_id)

    def update_balance_cache(self, user_id, current_balance):
        """ Redis 기반 포인트 잔액 업데이트

        Implements
            Argument로 입력받은 값들 캐시에 저장하기

        """
        return cache.set(f"{self.POINT_BALANCE_MAP}:{user_id}", current_balance, self.LOCK_LEASE_TIME)
