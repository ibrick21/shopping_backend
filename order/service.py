from .models import Order, OrderStatus
from .inventory_protocol import InventoryProtocol
from .repository_protocol import RepositoryProtocol
from .payment_manager_protocol import PaymentManagerProtocol
from .exceptions import OrderNotFoundError, AmountExceededError, InvalidOrderStatusError, PaymentNotFoundError,UserNotFoundError, ProductNotFoundError
from .decorators import logger
from .payment_manager import PaymentManager


class OrderService:
    def __init__(self,repository, inventory, payment_manager, user_repository, product_repository):
        self.repository = repository
        self.inventory = inventory
        self.payment_manager = payment_manager
        self.user_repository = user_repository
        self.product_repository = product_repository

    def create_order(self, user_id: int, product_id: int, quantity: int) -> Order | None:

        user = self.user_repository.find_user(user_id)

        product = self.product_repository.find_product(product_id)

        
        if user is None:
            raise UserNotFoundError("사용자를 찾을 수 없습니다.")

        if product is None:
            raise ProductNotFoundError("상품을 찾을 수 없습니다.")
        
        order = Order(
            user_id = user_id,
            product_id = product_id,
            price = product.price,
            quantity = quantity
        ) 

        self.inventory.decrease_stock(product.name, quantity)
          
        self.repository.add_order(order)

        return order
        
    
    @logger
    def pay_order(self, order_id: int) -> bool:
        order = self.repository.find_order(order_id)

        if order is None:
            raise OrderNotFoundError("주문을 찾을 수 없습니다.")

        if not order.can_pay():
            raise InvalidOrderStatusError("현재 주문 상태에서는 결제할 수 없습니다.")

        payment = self.payment_manager.find_payment(order.customer)

        if payment is None:
            raise PaymentNotFoundError("고객의 결제 정보를 찾을 수 없습니다.")

        total_price = order.price * order.quantity 

        if total_price >= 200000:
            raise AmountExceededError("10만 원 이상 주문은 바로 결제할 수 없습니다.")
        
        payment_success = payment.pay(total_price)

        if payment_success:
            order.pay()
            self.repository.update_order(order)
            return True

        self.cancel_order(order_id)
        return False

    def start_shipping(self, order_id: int) -> bool:
        order = self.repository.find_order(order_id)

        if order is None:
            raise OrderNotFoundError

        if not order.start_shipping():
            raise InvalidOrderStatusError

        return True

    def complete_delivery(self, order_id: int) -> bool:
        order = self.repository.find_order(order_id)

        if order is None:
            raise OrderNotFoundError

        if not order.complete_delivery():
            raise InvalidOrderStatusError

        return True
        
    @logger
    def cancel_order(self, order_id: int) -> bool:

        order = self.repository.find_order(order_id)

        if order is None:
            raise OrderNotFoundError("주문을 찾을 수 없습니다.")
        
        if order.cancel():
            self.repository.update_order(order)
            self.inventory.add_stock(order.product, order.quantity)
            return True

    def refund_order(self, order_id: int) -> bool:
        order = self.repository.find_order(order_id)

        if order is None:
            raise OrderNotFoundError

        if not order.can_refund():
            raise InvalidOrderStatusError

        payment = self.payment_manager.find_payment(order.customer)

        if payment is None:
            raise PaymentNotFoundError

        total_price = order.price * order.quantity

        payment.refund(total_price)

        self.inventory.add_stock(
            order.product,
            order.quantity
        )

        order.cancel()

        return True
    def change_order_product(
        self,
        order_id: int,
        new_product: str
    ) -> bool:
        order = self.repository.find_order(order_id)

        if order is None:
            return False

        return order.change_product(new_product)

    def get_paid_orders(self):
            return self.repository.get_paid_orders()
            


    def get_orders_by_status(self, status: OrderStatus):
        return self.repository.get_orders_by_status(status)

    def get_orders_by_min_price(self, min_price: int):
        return self.repository.get_orders_by_min_price(min_price)

    def get_orders(self, status: OrderStatus, min_price: int):
        for order in self.repository.orders:
            if order.status == status and order.price >= min_price:
                yield order

    