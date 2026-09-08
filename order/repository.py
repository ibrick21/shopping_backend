from .database import SessionLocal
from .orm_models import OrderDB
from .models import Order, OrderStatus
from sqlalchemy import select
from sqlalchemy.orm import Session

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
        self.session.commit()
        
        order.order_id =order_db.order_id

    def delete_order(self, order_id: int):
        order_db = self.session.get(OrderDB, order_id)

        if order_db is None:
            return False

        self.session.delete(order_db)
        self.session.commit()


    def update_order(self, order: Order):
        order_db = self.session.get(OrderDB, order.order_id)
        order_db.status = order.status.value

        self.session.commit()

    def get_paid_orders(self):
        yield from self.get_orders_by_status(OrderStatus.PAID)

   
    def get_orders_by_status(self, status: OrderStatus):
        stmt = select(OrderDB).where(
            OrderDB.status == status.value
       )

        order_dbs = self.session.scalars(stmt)  

        for order_db in order_dbs:
            yield self._order_db_to_order(order_db)     


    def get_orders_by_min_price(self, min_price: int):
        stmt = select(OrderDB).where(
            OrderDB.price >= min_price
        )
           
        order_dbs = self.session.scalars(stmt)
        
        for order_db in order_dbs:
            yield self._order_db_to_order(order_db)     
