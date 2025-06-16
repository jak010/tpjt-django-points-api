from typing import List, Dict

from django.core.cache import cache
from rest_framework.pagination import LimitOffsetPagination

from src.apps.models import PointBalance


class PointBalanceSyncJobConfig:
    class PaginateRequest:
        """ DRF의 LimitOffsetPagination을 사용하기 위한 임의 class """

        def __init__(self, limit: int, offset: int):
            self.query_params = {
                'limit': limit,
                'offset': offset
            }

    @classmethod
    def point_balance_sync_job(cls):
        """ 포인트 잔액 동기화 및 일별 리포트 생성 Job

        Implementation

            sync_point_balance_step()
            create_daily_point_report_step()

        """
        raise NotImplementedError()

    @classmethod
    def sync_point_balance_step(cls):
        """ DB의 포인트 잔액 정보를 Redis 캐시에 동기화하는 Step

        Implementation
            - Reader : 포인트 잔액 조회
            - Processor : 캐시 키 생성
            - Writer : Redis 포인트 잔액 저장
        """
        point_balances = cls.point_balance_reader()

        for point_balance in point_balances:
            point_balance_dict = cls.point_balance_processor(point_balance=point_balance)
            cls.point_balance_writer(point_balances=point_balance_dict)

    @classmethod
    def generate_daily_report_step(cls):
        """ 일별 리포트 생성 Step : 전일 포인트 트랜잭션을 집계하여 일별 리포트를 생성하는 Step

        Implementation
            - Reader : 포인트 잔액 조회
            - Processor : 일별 리포트 생성
            - Writer : DB 리포트 저장
        """
        ...

    @classmethod
    def point_balance_reader(cls) -> List[PointBalance]:
        """ 포인트 잔액 Reader

        Implementation
            ORM을 사용하여 DB에서 포인트 잔액 정보를 조회

            page 크기를 1000으로 하여 PointBalance 가져오기

        """

        limit_pagination = LimitOffsetPagination()
        return limit_pagination.paginate_queryset(
            PointBalance.objects.all(),
            PointBalanceSyncJobConfig.PaginateRequest(limit=1000, offset=0),
            None
        )

    @classmethod
    def point_balance_processor(cls, point_balance: PointBalance) -> dict:
        """ 포인트 잔액 Processor

        Implementation
            포인트 잔액을 Redis 캐시 키-값 쌍으로 전환

        """
        return {
            f"point:balanace:{point_balance.user_id}": int(point_balance.balance)
        }

    @classmethod
    def point_balance_writer(cls, point_balances: Dict[str, int]):
        """ 포인트 잔액 Writer

        Implementation
            Redis 캐시에 포인트 잔액 저장

        """

        cache_client = cache.client.get_client()
        for k, v in point_balances.items():
            cache_client.hset("point:balance", k, v)

    @classmethod
    def point_reader(cls):
        """ 포인트 Reader

        Implementation
            ORM을 사용하여 DB에서 전일 포인트 트랜잭션을 조회

        """
        ...

    @classmethod
    def point_processor(cls):
        """ 포인트 Processor

        Implementation
            포인트 트랜잭션을 사용자별로 집계하여 PointSumamry 생성

        """
        ...

    @classmethod
    def point_writer(cls):
        """ 포인트 Writer

        Implementation
            집계된 포인트 트랜잭션을 일별 리포트로 변환하여 DB에 저장
        """
        ...
