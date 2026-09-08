from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from order.repository import OrderRepository
from order.inventory import Inventory
from order.payment_manager import PaymentManager
from order.service import OrderService
from order.payment import Payment
from order.exceptions import InvalidOrderStatusError, OrderNotFoundError, UserNotFoundError
from fastapi import Depends
from sqlalchemy.orm import Session
from order.database import SessionLocal
from .user_repository import UserRepository
from order.models import User
from .product_repository import ProductRepository
from .product_service import ProductService
from .models import Product


app = FastAPI()

def get_session():
    session = SessionLocal()

    try:
        yield session

    finally:
        session.close()


inventory = Inventory()
payment_manager = PaymentManager()

jung_payment = Payment(140000)
kim_payment = Payment(70000)
payment_manager.add_payment("Kim", kim_payment)
payment_manager.add_payment("Jung", jung_payment)
inventory.add_stock("Keyboard", 10)

class CreateOrderRequest(BaseModel):
    user_id: int
    product_id: int
    quantity: int

class CreateUserRequest(BaseModel):
    name: str

class CreateProductRequest(BaseModel):
    name: str
    price: int
    stock: int

def get_repository(
    session: Session = Depends(get_session)
):
    repository = OrderRepository(session)

    return repository

def get_user_repository(
        session: Session = Depends(get_session)
):
    user_repository = UserRepository(session)

    return user_repository

def get_product_repository(
    session: Session = Depends(get_session)
):
    product_repository = ProductRepository(session)
    return product_repository


def get_service(session: Session = Depends(get_session)):

    repository = OrderRepository(session)

    user_repository = UserRepository(session)

    product_repository = ProductRepository(session)

    service =  OrderService(repository, inventory, payment_manager, user_repository, product_repository)

    return service

def get_product_service(
    session: Session = Depends(get_session)
):
    product_repository = ProductRepository(session)
    product_service = ProductService(product_repository)

    return product_service

@app.post("/orders")
def create_order(
    request: CreateOrderRequest,
    service: OrderService = Depends(get_service)
):
    try:

        order = service.create_order(
            request.user_id,
            request.product_id,
            request.quantity
        )

        return order
    except UserNotFoundError:
        raise HTTPException(
            status_code = 404,
            detail = "User Not Found"
        )

  
@app.post("/users")
def create_user(
    request: CreateUserRequest,
    user_repository: UserRepository = Depends(get_user_repository)
):
    
    user = User(
        name=request.name
    )

    user = user_repository.add_user(user)

    return user

@app.post("/products")
def create_product(
    request: CreateProductRequest,
    product_service: ProductService = Depends(get_product_service)
):

    product = product_service.create_product(
        name = request.name,
        price = request.price,
        stock = request.stock
    )

    return product

@app.get("/orders/{order_id}")
def get_order(
    order_id: int, 
    repository: OrderRepository = Depends(get_repository)
):
    

    order = repository.find_order(order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return order    

@app.post("/orders/{order_id}/pay")
def pay_order(
    order_id: int,
    service: OrderService = Depends(get_service)
):
    try:
        service.pay_order(order_id)

        return {"message": "Payment successful"}
    except InvalidOrderStatusError:
        raise HTTPException(
            status_code = 409,
            detail = "Order cannot be paid in current status"
        )
    except OrderNotFoundError:
        raise HTTPException(
            status_code = 404,
            detail = "Order not found"
        )

    return {"message": "Payment successful"}

@app.get("/orders")
def get_orders(
    min_price: int,
    repository: OrderRepository = Depends(get_repository)
):
    
    orders = repository.get_orders_by_min_price(min_price)

    return list(orders)

@app.delete("/orders/{order_id}")
def delete_order(
    order_id: int,
    repository: OrderRepository = Depends(get_repository)
):
    
    result = repository.delete_order(order_id)

    if not result:
        raise HTTPException(
            status_code = 404,
            detail = "Order not found"
        )
    return {"message": "Order deleted"}