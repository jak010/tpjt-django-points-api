import datetime

from django.db import models

from src.contrib.abstract.model import TimestampedModel


class DailyPointReport(TimestampedModel):
    class Meta:
        db_table = 'daily_point_reports'
        ordering = ['-created_at']

    user_id = models.BigIntegerField(null=False)
    report_date = models.DateField(null=False)  # 리포트 날짜
    earn_amount = models.BigIntegerField(null=False)  # 해당 날짜 동안 적립된 포인트 총액
    use_amount = models.BigIntegerField(null=False)  # 해당 날짜 동안 사용한 포인트 총액
    cancel_amount = models.BigIntegerField(null=False)  # 해당 날짜 동안 취소되어 되돌려 받은 포인트 총액
    net_amount = models.BigIntegerField(null=False)  # 순 포인트

    @classmethod
    def init_entity(cls,
                    user_id: int,
                    report_date: datetime.datetime,
                    earn_amount: int,
                    use_amount: int,
                    cancel_amount: int,
                    ):
        return cls(
            user_id=user_id,
            report_date=report_date,
            earn_amount=earn_amount,
            use_amount=use_amount,
            cancel_amount=cancel_amount,
            net_amount=earn_amount - use_amount + cancel_amount
        )
