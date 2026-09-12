from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Order, OrderStatus
from .orm_models import OrderDB


class OrderRepository:
    def __init__(self, session: Session):
         self.session = session

    def _order_db_to_order(self, order_db: OrderDB) -> Order:
        return Order(
            order_id = order_db.order_id,
            user_id = order_db.user_id,
            product_id = order_db.product_id,
            price = order_db.price,
            quantity = order_db.quantity,
            status = OrderStatus(order_db.status)
        )

         

    def find_order(self,order_id: int) -> Order | None:
        order_db = self.session.get(OrderDB, order_id)

        if order_db is None:
             return None

        return self._order_db_to_order(order_db)
    
    def add_order(self, order: Order):

        order_db = OrderDB(
            user_id = order.user_id,
            product_id= order.product_id,
            price = order.price,
            quantity = order.quantity,
            status = order.status.value
        )
        self.session.add(order_db)
        self.session.flush()
        
        order.order_id =order_db.order_id


    def update_order(self, order: Order):
        order_db = self.session.get(OrderDB, order.order_id)
        order_db.status = order.status.value


    def get_orders_by_user(self, user_id: int):
        stmt = select(OrderDB).where(
            OrderDB.user_id == user_id
        )

        order_dbs = self.session.scalars(stmt)

        for order_db in order_dbs:
            yield self._order_db_to_order(order_db)