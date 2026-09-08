from .payment import Payment
class PaymentManager:
    def __init__(self):
        self.payments = {}

    def add_payment(self,customer: str, payment:Payment):
        self.payments[customer] = payment

    def find_payment(self, customer: str):
        if customer in self.payments:
                return self.payments[customer]

        return None