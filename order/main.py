from order.repository import OrderRepository
from order.service import OrderService
from order.inventory import Inventory
from order.payment import Payment
from order.payment_manager import PaymentManager
from order.exceptions import OrderNotFoundError, AmountExceededError, InvalidOrderStatusError

repository = OrderRepository()
inventory = Inventory()
payment_manager = PaymentManager()
kim_payment = Payment(70000)
lee_payment = Payment(90000)
payment_manager.add_payment("Kim", kim_payment)
payment_manager.add_payment("Lee", lee_payment)
service = OrderService(repository, inventory, payment_manager)

inventory.add_stock("Keyboard",10)
order1 = service.create_order("Kim", "Keyboard", 20000, 2)
service.pay_order(1)
order2 = service.create_order("Lee", "Keyboard", 15000, 3)
service.pay_order(2)
print()