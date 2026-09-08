from .payment import Payment

class FakePaymentManager:
    def __init__(self, payment: Payment):
        self.payment = payment

    def find_payment(self, customer: str) -> Payment:
        return self.payment