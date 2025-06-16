from dataclasses import dataclass


@dataclass
class PointSummary:
    user_id: int
    earn_amount: int
    use_amount: int
    cancel_amount: int

    def add_earn_amount(self, amount):
        self.earn_amount += amount

    def add_use_amount(self, amount):
        self.use_amount += amount

    def add_cancel_amount(self, amount):
        self.cancel_amount += amount
