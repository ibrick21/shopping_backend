from typing import Protocol
from .models import Order, OrderStatus

class RepositoryProtocol(Protocol):
    def add_order(self, order: Order):
        ...

    def find_order(self, order_id: int) -> Order | None:
        ...

    def get_paid_orders(self):
        ...

    def get_orders_by_status(self, status: OrderStatus):
        ...
             
    def get_orders_by_min_price(self, min_price: int):
        ...
        