from enum import Enum

from django.db import models

from src.contrib.abstract.model import TimestampedModel
from .point_balance import PointBalance


class Point(TimestampedModel):
    class Meta:
        db_table = 'points'
        ordering = ['-created_at']

    class Type(Enum):
        EARN = "EARN"
        USED = "USED"
        CANCELED = "CANCELED"

    id = models.PositiveBigIntegerField(primary_key=True)
    user_id = models.PositiveBigIntegerField(null=False)
    amount = models.PositiveBigIntegerField(null=False)
    type = models.CharField(
        choices=[(t.name, t.value) for t in Type],
        null=False,
        max_length=50
    )
    description = models.CharField(max_length=255, null=False)
    balance_snapshot = models.PositiveBigIntegerField(null=False)
    version = models.PositiveBigIntegerField(default=0)

    point_balance = models.ForeignKey(PointBalance, name="point_balance", on_delete=models.CASCADE)
