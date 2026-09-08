from typing import Protocol
from .payment import Payment

class PaymentManagerProtocol(Protocol):
    def find_payment(self, customer: str) -> Payment | None:
        ...
        