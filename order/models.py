from dataclasses import dataclass
from enum import Enum
from .exceptions import InvalidOrderStatusError

class OrderStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELED = "canceled"
    SHIPPING = "shipping"
    DELIVERED = "delivered"


@dataclass
class Order:
    user_id: int
    product_id: int
    price: int
    quantity: int
    order_id: int | None = None
    status: OrderStatus = OrderStatus.PENDING



    def __post_init__(self):
        if self.price <= 0:
            raise ValueError("가격은 0보다 커야 합니다.")

    def __post_init__(self):
        if self.order_id is not None and self.order_id <= 0:
            raise ValueError("주문 ID는 1 이상이어야 합니다.")

        if self.quantity <= 0:
                    raise ValueError("주문 수량은 1개 이상이어야 합니다.")
        
    def pay(self):
        if self.status != OrderStatus.PENDING:
            raise InvalidOrderStatusError("현재 주문 상태에서는 결제할 수 없습니다.")

        self.status = OrderStatus.PAID
        return True

    def can_pay(self) -> bool:
        if self.status == OrderStatus.PENDING:
            return True
        return False

    def cancel(self):
        if self.status == OrderStatus.PENDING or self.status == OrderStatus.PAID:
            self.status = OrderStatus.CANCELED
            return True

        return False

    def can_refund(self) -> bool:
        if self.status == OrderStatus.PAID:
            return True

        return False

    def change_product(self, new_product: str) -> bool:  
        if self.status == OrderStatus.PENDING and new_product !="":
            self.product = new_product
            return True

        return False  

    def start_shipping(self):
            if self.status == OrderStatus.PAID: 
    
                self.status = OrderStatus.SHIPPING
                return True
    
            return False

    def complete_delivery(self):
        if self.status == OrderStatus.SHIPPING:
            self.status = OrderStatus.DELIVERED
            return True

        return False

       
@dataclass
class DeliveryOrder(Order):
    address: str = ""

    def pay(self):
        if self.address == "":
            return False

        return super().pay()

    def change_address(self,new_address: str) -> bool:
        if self.status != OrderStatus.PENDING:
            return False

        self.address = new_address
        return True

    
@dataclass
class PickupOrder(Order):
    pickup_store: str = ""

    def pay(self):
        if self.pickup_store == "":
            return False

        return super().pay()

    def change_pickup_store(self,new_store: str) -> bool:
        if  self.status == OrderStatus.PENDING and new_store != "":   
            self.pickup_store = new_store
            return True

        return False



@dataclass
class User:
    name: str
    email: str
    password_hash: str
    user_id: int | None = None


@dataclass
class Product:
    name:str
    price: int
    stock: int
    product_id: int |  None = None
