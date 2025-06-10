from django.db import models, transaction, IntegrityError

from src.contrib.abstract.model import TimestampedModel
import backoff

from src.apps.service.exceptions import OptimisticLockingError


class PointBalance(TimestampedModel):
    class Meta:
        db_table = 'point_balances'
        ordering = ['-created_at']

    id = models.BigAutoField(primary_key=True)
    user_id = models.PositiveBigIntegerField(null=False, unique=True)
    balance = models.DecimalField(null=False, default=0, decimal_places=10, max_digits=19)
    version = models.PositiveBigIntegerField(default=1)

    @classmethod
    def initialized(cls, user_id: int, balance: float):
        return cls(
            user_id=user_id,
            balance=balance
        )

    def update_with_optimistic_lock(self):
        """ Optimistic Locking 구현

        Note:
            add_balance() 수행 후, 증가분의 금액만큼 Optimistic Lock으로 처리하기 위해 구현된 함수ㅁ

        """
        if self.pk:
            updated = PointBalance.objects.filter(
                pk=self.pk,
                version=self.version
            ).update(
                balance=self.balance,
                version=models.F("version") + 1
            )
            if updated == 0:
                raise OptimisticLockingError()

            return PointBalance.objects.get(id=self.id)

    def add_balance(self, amount: float):
        """ 잔액을 추가합니다. """
        if amount <= 0:
            raise Exception("amount must be positive")

        if self.balance is None:
            self.balance = 0

        self.balance += amount
        return self

    @backoff.on_exception(backoff.expo, OptimisticLockingError, max_time=3, max_tries=3)
    def add_balance_with_optimistic_lock(self, amount: float):
        """ 잔액을 추가합니다. """
        if amount <= 0:
            raise Exception("amount must be positive")

        with transaction.atomic():
            update_count = PointBalance.objects.filter(user_id=self.user_id, version=self.version) \
                .update(
                balance=models.F("balance") + amount,
                version=models.F("version") + 1
            )
            if update_count == 0:
                self.refresh_from_db()

        return PointBalance.objects.get(id=self.id)

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
