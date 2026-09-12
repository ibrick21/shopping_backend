from .decorators import logger
from .exceptions import (
    AmountExceededError,
    InsufficientStockError,
    InvalidOrderStatusError,
    OrderAccessDeniedError,
    OrderNotFoundError,
    PaymentNotFoundError,
    ProductNotFoundError,
    UserNotFoundError,
)
from .models import Order, OrderStatus
from .payment import Payment, PaymentStatus


class OrderService:
    def __init__(self,repository, payment_repository, user_repository, product_repository):
        self.repository = repository
        self.payment_repository = payment_repository
        self.user_repository = user_repository
        self.product_repository = product_repository

    def create_order(self, user_id: int, product_id: int, quantity: int) -> Order | None:

        user = self.user_repository.find_user(user_id)

        product = self.product_repository.find_product(product_id)

        
        if user is None:
            raise UserNotFoundError("사용자를 찾을 수 없습니다.")

        if product is None:
            raise ProductNotFoundError("상품을 찾을 수 없습니다.")

        if product.stock < quantity:
            raise InsufficientStockError("재고가 부족합니다.")
        
        order = Order(
            user_id = user_id,
            product_id = product_id,
            price = product.price,
            quantity = quantity
        ) 

        self.product_repository.decrease_stock(product_id, quantity)
          
        self.repository.add_order(order)

        return order

    def get_order(self, order_id: int, user_id: int) -> Order:
        order = self.repository.find_order(order_id)

        if order is None:
            raise OrderNotFoundError("주문을 찾을 수 없습니다.")

        if order.user_id != user_id:
            raise OrderAccessDeniedError("주문에 접근할 권한이 없습니다.")

        return order

    def get_my_orders(self, user_id: int):
        return self.repository.get_orders_by_user(user_id)
    
    @logger
    def pay_order(self, order_id: int, user_id: int) -> bool:

        order = self.get_order(order_id, user_id)

        if not order.can_pay():
            raise InvalidOrderStatusError(
                "현재 주문 상태에서는 결제할 수 없습니다."
            )

        total_price = order.price * order.quantity

        if total_price >= 200000:
            raise AmountExceededError(
                "20만 원 이상 주문은 바로 결제할 수 없습니다."
            )

        payment = Payment(
            order_id=order.order_id,
            amount=total_price,
            status=PaymentStatus.PAID
        )

        self.payment_repository.add_payment(payment)

        order.pay()
        self.repository.update_order(order)

        return True

    def start_shipping(self, order_id: int) -> bool:
        order = self.repository.find_order(order_id)

        if order is None:
            raise OrderNotFoundError

        if not order.start_shipping():
            raise InvalidOrderStatusError

        self.repository.update_order(order)
        return True

    def complete_delivery(self, order_id: int) -> bool:
        order = self.repository.find_order(order_id)

        if order is None:
            raise OrderNotFoundError

        if not order.complete_delivery():
            raise InvalidOrderStatusError
        
        self.repository.update_order(order)

        return True
        
    @logger
    def cancel_order(self, order_id: int, user_id: int) -> bool:

        order = self.get_order(order_id, user_id)

        product = self.product_repository.find_product(order.product_id)

        if product is None:
            raise ProductNotFoundError("상품을 찾을 수 없습니다.")
        
 
        if order.cancel():

            self.repository.update_order(order)

            self.product_repository.increase_stock(product.product_id, order.quantity)
            
            return True

        raise InvalidOrderStatusError("현재 주문 상태에서는 취소할 수 없습니다.")

    def refund_order(self, order_id: int, user_id: int) -> bool:

        order = self.get_order(order_id, user_id)


        if not order.can_refund():
            raise InvalidOrderStatusError(
                "현재 주문 상태에서는 환불할 수 없습니다."
            )
        payment = self.payment_repository.find_paid_payment(order_id)

        if payment is None:
            raise PaymentNotFoundError(
                "결제 기록을 찾을 수 없습니다."
            )

        payment.refund()

        self.payment_repository.update_payment(payment)

        product = self.product_repository.find_product(
            order.product_id
        )

        if product is None:
            raise ProductNotFoundError(
                "상품을 찾을 수 없습니다."
            )

        self.product_repository.increase_stock(
            order.product_id,
            order.quantity
        )

        order.refund()
        self.repository.update_order(order)

        return True
    
    