import pytest

from order.exceptions import InvalidOrderStatusError, OrderNotFoundError
from order.models import OrderStatus
from order.repository import OrderRepository
from order.inventory import Inventory
from order.payment import Payment
from order.fake_payment_manager import FakePaymentManager
from order.service import OrderService


@pytest.fixture
def payment():
    return Payment(70000)


def test_pay_order_success(payment):
    repository = OrderRepository()
    inventory = Inventory()

    fake_payment_manager = FakePaymentManager(payment)

    service = OrderService(
        repository,
        inventory,
        fake_payment_manager
    )

    inventory.add_stock("Keyboard", 10)
    order = service.create_order("Kim", "Keyboard", 20000, 2)

    service.pay_order(1)

    assert order.status == OrderStatus.PAID
    assert payment.balance == 30000


def test_pay_order_insufficient_balance():
    repository = OrderRepository()
    inventory = Inventory()

    payment = Payment(30000)
    fake_payment_manager = FakePaymentManager(payment)

    service = OrderService(
        repository,
        inventory,
        fake_payment_manager
    )

    inventory.add_stock("Keyboard", 10)
    order = service.create_order("Kim", "Keyboard", 20000, 2)

    service.pay_order(1)

    assert order.status == OrderStatus.CANCELED
    assert payment.balance == 30000
    assert inventory.stocks["Keyboard"] == 10


def test_duplicate_payment(payment):
    repository = OrderRepository()
    inventory = Inventory()

    fake_payment_manager = FakePaymentManager(payment)

    service = OrderService(
        repository,
        inventory,
        fake_payment_manager
    )

    inventory.add_stock("Keyboard", 10)
    order = service.create_order("Kim", "Keyboard", 20000, 2)

    # 첫 번째 결제
    service.pay_order(1)

    assert order.status == OrderStatus.PAID
    assert payment.balance == 30000

    # 두 번째 결제
    with pytest.raises(InvalidOrderStatusError):
        service.pay_order(1)

    # 두 번째 결제에서 돈이 추가로 빠지지 않았는지 확인
    assert payment.balance == 30000


def test_pay_order_not_found(payment):
    repository = OrderRepository()
    inventory = Inventory()

    fake_payment_manager = FakePaymentManager(payment)

    service = OrderService(
        repository,
        inventory,
        fake_payment_manager
    )

    with pytest.raises(OrderNotFoundError):
        service.pay_order(999)\


def test_start_shipping_success(payment):

    repository = OrderRepository()
    inventory = Inventory()
    fake_payment_manager = FakePaymentManager(payment)

    service = OrderService(
            repository,
            inventory,
            fake_payment_manager
    )
    
    inventory.add_stock("Keyboard", 10)

    order = service.create_order(
        "Kim",
        "Keyboard",
        20000,
        2
    )

    service.pay_order(1)
    service.start_shipping(1)

    assert order.status == OrderStatus.SHIPPING


def test_start_shipping_success(payment):

    repository = OrderRepository()
    inventory = Inventory()
    fake_payment_manager = FakePaymentManager(payment)

    service = OrderService(
            repository,
            inventory,
            fake_payment_manager
    )
    
    inventory.add_stock("Keyboard", 10)

    order = service.create_order(
        "Kim",
        "Keyboard",
        20000,
        2
    )


    with pytest.raises(InvalidOrderStatusError):
        service.start_shipping(1)
