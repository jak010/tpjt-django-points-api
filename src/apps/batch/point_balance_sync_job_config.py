import datetime
from datetime import timedelta
from typing import List, Dict

from django.core.cache import cache
from rest_framework.pagination import LimitOffsetPagination

from src.apps.models import PointBalance, Point
from src.apps.models.daily_report import DailyPointReport
from src.apps.models.point_summary import PointSummary


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
            generate_daily_point_report_step()

        """
        cls.sync_point_balance_step()
        cls.generate_daily_report_step()

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

        daily_points = cls.point_reader()
        point_summaries = cls.point_processor(points=daily_points)

        cls.report_writer(point_summaries=point_summaries)

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
    def point_reader(cls) -> List[Point]:
        """ 포인트 Reader

        Implementation
            ORM을 사용하여 DB에서 전일 포인트 트랜잭션을 조회

        """
        _current = datetime.datetime.now()
        start_time = _current.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = _current.replace(hour=23, minute=59, second=59, microsecond=0)

        return Point.objects.filter(
            created_at__gte=start_time,
            created_at__lte=end_time
        ).all()

    @classmethod
    def point_processor(cls, points: List[Point]) -> List[PointSummary]:
        """ 포인트 Processor

        Implementation
            포인트 트랜잭션을 사용자별로 집계하여 PointSumamry 생성

        """
        results = []
        for point in points:
            if point.type == Point.Type.EARN.value:
                results.append(PointSummary(point.user_id, point.amount, 0, 0))
            if point.type == Point.Type.USED.value:
                results.append(PointSummary(point.user_id, 0, point.amount, 0))
            if point.type == Point.Type.CANCELED.value:
                results.append(PointSummary(point.user_id, 0, 0, point.amount))
        return results

    @classmethod
    def report_writer(cls, point_summaries: List[PointSummary]):
        """ 포인트 Writer

        Implementation
            집계된 포인트 트랜잭션을 일별 리포트로 변환하여 DB에 저장
        """

        for point_summary in point_summaries:

            daily_point = DailyPointReport.objects.filter(
                user_id=point_summary.user_id,
                report_date=datetime.datetime.now() - timedelta(days=1)
            ).first()

            if daily_point:
                daily_point.earn_amount += point_summary.earn_amount
                daily_point.use_amount += point_summary.use_amount
                daily_point.cancel_amount = point_summary.cancel_amount
                daily_point.save()
            else:
                new_obj = DailyPointReport.init_entity(
                    user_id=point_summary.user_id,
                    report_date=datetime.datetime.now() - timedelta(days=1),  # 전일 데이터
                    earn_amount=point_summary.earn_amount,
                    use_amount=point_summary.use_amount,
                    cancel_amount=point_summary.cancel_amount
                )
                new_obj.save()
