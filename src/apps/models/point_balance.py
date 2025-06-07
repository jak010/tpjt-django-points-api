from django.db import models

from src.contrib.abstract.model import TimestampedModel


class PointBalance(TimestampedModel):
    class Meta:
        db_table = 'point_balances'
        ordering = ['-created_at']

    id = models.BigAutoField(primary_key=True)
    user_id = models.PositiveBigIntegerField(null=False, unique=True)
    balance = models.DecimalField(null=False, default=0, decimal_places=10, max_digits=19)
    version = models.PositiveBigIntegerField(default=0)

    @classmethod
    def initialized(cls, user_id: int, balance: float):
        return cls(
            user_id=user_id,
            balance=balance,
            version=0,
        )

    def add_balance(self, amount: float):
        """ 잔액을 추가합니다. """
        if amount <= 0:
            raise Exception("amount must be positive")

        if self.balance is None:
            self.balance = 0

        self.balance += amount

    def subtract_balance(self, amount: float):
        """ 잔액을 차감합니다. """
        if amount <= 0:
            raise Exception("amount must be positive")

        if self.balance is None:
            self.balance = 0

        if self.balance < amount:
            raise Exception("insufficient balance")

        self.balance -= amount

    def set_balance(self, balance: float):
        """ 잔액을 설정합니다. """
        if self.balance is None or self.balance < 0:
            raise Exception("balance cannot be negarive or null")
        self.balance = balance
