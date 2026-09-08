from order.database import SessionLocal
from order.orm_models import OrderDB
from order.exceptions import OrderNotFoundError
session = SessionLocal()

order = OrderDB(
    customer="Kim",
    product="Mouse",
    price=30000,
    quantity=1,
    status="pending"
)

order = session.get(OrderDB,9)

if order is None:
    raise OrderNotFoundError

else:
    session.delete(order)
    session.commit