from django.db import models

from src.contrib.abstract.model import TimestampedModel


class PointBalance(TimestampedModel):
    class Meta:
        db_table = 'point_balances'
        ordering = ['-created_at']

    id = models.PositiveBigIntegerField(primary_key=True)
    user_id = models.PositiveBigIntegerField(null=False, unique=True)
    balance = models.DecimalField(null=False, default=0, decimal_places=10, max_digits=19)
    version = models.PositiveBigIntegerField(default=0)
