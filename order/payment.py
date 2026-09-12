from dataclasses import dataclass
from enum import Enum


class PaymentStatus(Enum):
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"

@dataclass
class Payment:
    order_id: int
    amount: int
    status: PaymentStatus
    payment_id: int | None = None

    def refund(self):
        if self.status != PaymentStatus.PAID:
            return False

        self.status = PaymentStatus.REFUNDED
        return True