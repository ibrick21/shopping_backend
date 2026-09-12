import pytest

from order.models import Order, OrderStatus, User, Product
from order.payment import Payment, PaymentStatus
from order.service import OrderService
from order.exceptions import (
    InvalidOrderStatusError,
    OrderNotFoundError,
    OrderAccessDeniedError,
    InsufficientStockError,
    ProductNotFoundError,
    PaymentNotFoundError,
)


# =========================================================
# Fake Repositories
# 실제 PostgreSQL 대신 테스트용 메모리를 사용한다.
# =========================================================

class FakeOrderRepository:

    def __init__(self):
        self.orders = {}
        self.next_id = 1

    def add_order(self, order: Order):
        order.order_id = self.next_id
        self.orders[self.next_id] = order
        self.next_id += 1

    def find_order(self, order_id: int):
        return self.orders.get(order_id)

    def update_order(self, order: Order):
        self.orders[order.order_id] = order

    def get_orders_by_user(self, user_id: int):
        for order in self.orders.values():
            if order.user_id == user_id:
                yield order


class FakeUserRepository:

    def __init__(self):
        self.users = {}

    def add_user(self, user: User):
        self.users[user.user_id] = user

    def find_user(self, user_id: int):
        return self.users.get(user_id)


class FakeProductRepository:

    def __init__(self):
        self.products = {}

    def add_product(self, product: Product):
        self.products[product.product_id] = product

    def find_product(self, product_id: int):
        return self.products.get(product_id)

    def decrease_stock(self, product_id: int, quantity: int):
        self.products[product_id].stock -= quantity

    def increase_stock(self, product_id: int, quantity: int):
        self.products[product_id].stock += quantity


class FakePaymentRepository:

    def __init__(self):
        self.payments = {}
        self.next_id = 1

    def add_payment(self, payment: Payment):
        payment.payment_id = self.next_id
        self.payments[self.next_id] = payment
        self.next_id += 1

    def find_paid_payment(self, order_id: int):
        for payment in self.payments.values():
            if (
                payment.order_id == order_id
                and payment.status == PaymentStatus.PAID
            ):
                return payment

        return None

    def update_payment(self, payment: Payment):
        self.payments[payment.payment_id] = payment


# =========================================================
# Fixture
# 매 테스트마다 깨끗한 Service + Fake Repository를 만든다.
# =========================================================

@pytest.fixture
def setup_service():

    order_repository = FakeOrderRepository()
    payment_repository = FakePaymentRepository()
    user_repository = FakeUserRepository()
    product_repository = FakeProductRepository()

    service = OrderService(
        order_repository,
        payment_repository,
        user_repository,
        product_repository
    )

    user = User(
        name="Kim",
        email="kim@test.com",
        password_hash="test_hash",
        user_id=1
    )

    product = Product(
        name="Keyboard",
        price=20000,
        stock=10,
        product_id=1
    )

    user_repository.add_user(user)
    product_repository.add_product(product)

    return (
        service,
        order_repository,
        payment_repository,
        user_repository,
        product_repository
    )


# =========================================================
# 주문 생성
# =========================================================

def test_create_order_success(setup_service):

    service, order_repository, _, _, product_repository = setup_service

    order = service.create_order(
        user_id=1,
        product_id=1,
        quantity=2
    )

    assert order.order_id == 1
    assert order.user_id == 1
    assert order.product_id == 1
    assert order.price == 20000
    assert order.quantity == 2
    assert order.status == OrderStatus.PENDING

    # 재고 10 -> 8
    product = product_repository.find_product(1)
    assert product.stock == 8


def test_create_order_insufficient_stock(setup_service):

    service, _, _, _, product_repository = setup_service

    with pytest.raises(InsufficientStockError):
        service.create_order(
            user_id=1,
            product_id=1,
            quantity=20
        )

    # 주문 실패했으므로 재고도 그대로
    product = product_repository.find_product(1)
    assert product.stock == 10


def test_create_order_product_not_found(setup_service):

    service, _, _, _, _ = setup_service

    with pytest.raises(ProductNotFoundError):
        service.create_order(
            user_id=1,
            product_id=999,
            quantity=1
        )


# =========================================================
# 주문 조회 / Authorization
# =========================================================

def test_get_order_success(setup_service):

    service, _, _, _, _ = setup_service

    order = service.create_order(
        user_id=1,
        product_id=1,
        quantity=2
    )

    result = service.get_order(
        order_id=order.order_id,
        user_id=1
    )

    assert result.order_id == order.order_id
    assert result.user_id == 1


def test_get_order_not_found(setup_service):

    service, _, _, _, _ = setup_service

    with pytest.raises(OrderNotFoundError):
        service.get_order(
            order_id=999,
            user_id=1
        )


def test_get_order_access_denied(setup_service):

    service, _, _, _, _ = setup_service

    order = service.create_order(
        user_id=1,
        product_id=1,
        quantity=2
    )

    # user_id=2가 user_id=1의 주문을 조회
    with pytest.raises(OrderAccessDeniedError):
        service.get_order(
            order_id=order.order_id,
            user_id=2
        )


# =========================================================
# 결제
# =========================================================

def test_pay_order_success(setup_service):

    service, order_repository, payment_repository, _, _ = setup_service

    order = service.create_order(
        user_id=1,
        product_id=1,
        quantity=2
    )

    service.pay_order(
        order_id=order.order_id,
        user_id=1
    )

    saved_order = order_repository.find_order(order.order_id)

    assert saved_order.status == OrderStatus.PAID

    payment = payment_repository.find_paid_payment(order.order_id)

    assert payment is not None
    assert payment.amount == 40000
    assert payment.status == PaymentStatus.PAID


def test_duplicate_payment(setup_service):

    service, _, _, _, _ = setup_service

    order = service.create_order(
        user_id=1,
        product_id=1,
        quantity=2
    )

    service.pay_order(
        order_id=order.order_id,
        user_id=1
    )

    with pytest.raises(InvalidOrderStatusError):
        service.pay_order(
            order_id=order.order_id,
            user_id=1
        )


def test_pay_other_users_order(setup_service):

    service, _, _, _, _ = setup_service

    order = service.create_order(
        user_id=1,
        product_id=1,
        quantity=2
    )

    with pytest.raises(OrderAccessDeniedError):
        service.pay_order(
            order_id=order.order_id,
            user_id=2
        )


# =========================================================
# 주문 취소
# =========================================================

def test_cancel_order_success(setup_service):

    service, order_repository, _, _, product_repository = setup_service

    order = service.create_order(
        user_id=1,
        product_id=1,
        quantity=2
    )

    # 주문하면서 10 -> 8
    assert product_repository.find_product(1).stock == 8

    service.cancel_order(
        order_id=order.order_id,
        user_id=1
    )

    saved_order = order_repository.find_order(order.order_id)

    assert saved_order.status == OrderStatus.CANCELED

    # 취소하면서 8 -> 10
    assert product_repository.find_product(1).stock == 10


# =========================================================
# 환불
# =========================================================

def test_refund_order_success(setup_service):

    service, order_repository, payment_repository, _, product_repository = setup_service

    order = service.create_order(
        user_id=1,
        product_id=1,
        quantity=2
    )

    service.pay_order(
        order_id=order.order_id,
        user_id=1
    )

    # 결제 완료 상태
    assert order.status == OrderStatus.PAID
    assert product_repository.find_product(1).stock == 8

    service.refund_order(
        order_id=order.order_id,
        user_id=1
    )

    saved_order = order_repository.find_order(order.order_id)

    assert saved_order.status == OrderStatus.CANCELED

    # 재고 복원
    assert product_repository.find_product(1).stock == 10

    # PAID인 payment는 더 이상 없어야 함
    assert payment_repository.find_paid_payment(order.order_id) is None

    payment = payment_repository.payments[1]

    assert payment.status == PaymentStatus.REFUNDED


def test_refund_pending_order(setup_service):

    service, _, _, _, _ = setup_service

    order = service.create_order(
        user_id=1,
        product_id=1,
        quantity=2
    )

    # 결제하지 않은 PENDING 주문
    with pytest.raises(InvalidOrderStatusError):
        service.refund_order(
            order_id=order.order_id,
            user_id=1
        )