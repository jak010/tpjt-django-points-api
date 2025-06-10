from django.core.cache import cache


class PointRedisService:
    POINT_BALANCE_MAP = 'point:balance'  # 포인트 잔액 저장 키값
    POINT_LOCK_PREFIX = "point:lock:"
    LOCK_WAIT_TIME = 3
    LOCK_LEASE_TIME = 3

    def __init__(self):

    def earn_point(self, user_id):
        """ Redis 기반 포인트 적립 처리

        Implements
            분산 락 획득 -> 캐시된 잔액 조회 (없으면 DB에서 조회) -> 포인트 잔액 증가 -> DB 저장 및 캐시 업데이트 -> 포인트 인력 저장

        """

        # 분산 락 획득
        # with cache.lock(f"{self.POINT_LOCK_PREFIX}:{user_id}", timeout=2, blocking_timeout=2) as lock:
        #     ...

        ...

    def use_point(self): ...

    def cancel_point(self): ...
