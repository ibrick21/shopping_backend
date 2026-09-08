from order.database import SessionLocal
from order.orm_models import UserDB, OrderDB

session = SessionLocal()

user_db = session.get(UserDB, 1)

print(user_db.name)
print(user_db.orders)

for order_db in user_db.orders:
    print(order_db.order_id, order_db.product)

session.close()