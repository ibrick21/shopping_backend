from sqlalchemy import select
from sqlalchemy.orm import Session

from .orm_models import PaymentDB
from .payment import Payment, PaymentStatus


class PaymentRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_payment(self, payment: Payment):

        payment_db = PaymentDB(
            order_id=payment.order_id,
            amount=payment.amount,
            status=payment.status.value
        )

        self.session.add(payment_db)
        self.session.flush()

        payment.payment_id = payment_db.payment_id

    def find_paid_payment(self, order_id: int) -> Payment | None:
        stmt = select(PaymentDB).where(
            PaymentDB.order_id == order_id,
            PaymentDB.status == PaymentStatus.PAID.value
        )

        payment_db = self.session.scalars(stmt).first()

        if payment_db is None:
            return None

        return Payment(
            payment_id=payment_db.payment_id,
            order_id=payment_db.order_id,
            amount=payment_db.amount,
            status=PaymentStatus(payment_db.status)
        )


    def update_payment(self, payment: Payment):
        payment_db = self.session.get(
            PaymentDB,
            payment.payment_id
        )

        payment_db.status = payment.status.value

        