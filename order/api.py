from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from order.repository import OrderRepository
from order.service import OrderService
from fastapi import Depends
from sqlalchemy.orm import Session
from order.database import SessionLocal
from .user_service import UserService
from order.models import User, Product
from .user_repository import UserRepository
from .product_repository import ProductRepository
from .payment_repository import PaymentRepository
from .product_service import ProductService
from .security import decode_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from order.exceptions import PaymentNotFoundError, AmountExceededError, InvalidOrderStatusError, OrderNotFoundError, UserNotFoundError,UserExistError,InvalidCredentialsError, InvalidTokenError, OrderAccessDeniedError, ProductNotFoundError
from fastapi import Depends
app = FastAPI()

bearer_scheme = HTTPBearer()

def get_session():
    session = SessionLocal()

    try:
        yield session

    finally:
        session.close()


class CreateOrderRequest(BaseModel):
    product_id: int
    quantity: int

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class CreateProductRequest(BaseModel):
    name: str
    price: int
    stock: int

class UserResponse(BaseModel):
    user_id: int
    name: str
    email: str

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

    payment_repository = PaymentRepository(session)

    user_repository = UserRepository(session)

    product_repository = ProductRepository(session)

    service =  OrderService(repository, payment_repository, user_repository, product_repository)

    return service

def get_user_service(session: Session = Depends(get_session)):


    user_repository = UserRepository(session)

    user_service = UserService(user_repository)

    return user_service

def get_product_service(
    session: Session = Depends(get_session)
):
    product_repository = ProductRepository(session)

    product_service = ProductService(product_repository)

    return product_service


def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        user_repository : UserRepository = Depends(get_user_repository)
):


    try:
        token = credentials.credentials

        user_id = decode_access_token(token)
        user = user_repository.find_user(user_id)

        if user is None:
            raise HTTPException(
                status_code = 401, 
                detail = "유효하지 않은 토큰"
            )

        return user

    except InvalidTokenError:
        raise HTTPException(
            status_code = 401,
            detail = "유효하지 않은 토큰"
        )


  
@app.post("/auth/signup", response_model = UserResponse)
def sign_up(
    request: SignupRequest,
    user_service: UserService = Depends(get_user_service)
):

    try:
        user = user_service.sign_up(
            name = request.name,
            email = request.email,
            password = request.password
        )

        return user
    
    except UserExistError:
        raise HTTPException(
            status_code = 409,
            detail = "Email already exists"
        )

@app.post("/auth/login")
def login(
    request: LoginRequest,
    service: UserService = Depends(get_user_service)
):

    try:
        token = service.login(request.email,request.password)

        return {
            "access_token": token,
            "token_type": "bearer"
        }

    except InvalidCredentialsError:
        raise HTTPException(
            status_code = 401,
            detail = "로그인 실패"
        )


@app.post("/order")
def create_order(
    request: CreateOrderRequest,
    service: OrderService = Depends(get_service),
    current_user: User = Depends(get_current_user)
):
    try:

        order = service.create_order(
            current_user.user_id,
            request.product_id,
            request.quantity
        )

        return order
    except UserNotFoundError:
        raise HTTPException(
            status_code = 404,
            detail = "User Not Found"
        )

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

@app.post("/orders/{order_id}/pay")
def pay_order(
    order_id: int,
    service: OrderService = Depends(get_service),
     current_user: User = Depends(get_current_user)
):
    try:
        service.pay_order(order_id, current_user.user_id)

        return {"message": "Payment successful"}
    
    except OrderNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    except OrderAccessDeniedError:
        raise HTTPException(
            status_code=403,
            detail="Forbidden"
        )

    except InvalidOrderStatusError:
        raise HTTPException(
            status_code=400,
            detail="Order cannot be paid"
        )

    except AmountExceededError:
        raise HTTPException(
            status_code=400,
            detail="Payment amount exceeded"
        )


@app.get("/me")
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user

@app.get("/orders")
def get_my_orders(
    service: OrderService = Depends(get_service),
    current_user: User = Depends(get_current_user)
):
    return list(
        service.get_my_orders(current_user.user_id)
    )


@app.get("/orders/{order_id}")
def get_order(
    order_id: int, 
    service: OrderService = Depends(get_service),
    current_user: User = Depends(get_current_user)
):
    
    try:
        order = service.get_order(order_id, current_user.user_id)

        return order

    except OrderNotFoundError:
        raise HTTPException(
            status_code = 404,
            detail = "Order not found"
        )

    except OrderAccessDeniedError:
        raise HTTPException(
            status_code = 403,
            detail = "Forbidden"
        )   

@app.get("/orders")
def get_my_orders(
    service: OrderService = Depends(get_service),
    current_user: User = Depends(get_current_user)
):
    return list(
        service.get_my_orders(current_user.user_id)
    )

@app.delete("/orders/{order_id}")
def delete_order(
    order_id: int,
    service: OrderService = Depends(get_service),
    current_user : User = Depends(get_current_user)
):

    try:
        service.cancel_order(
            order_id,
            current_user.user_id
        )

        return {"message": "Order deleted"}

    except OrderNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    except OrderAccessDeniedError:
        raise HTTPException(
            status_code=403,
            detail="Forbidden"
        )

    except ProductNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    except InvalidOrderStatusError:
        raise HTTPException(
            status_code=400,
            detail="Order cannot be canceled"
        )

@app.post("/orders/{order_id}/refund")
def refund_order(
    order_id: int,
    service: OrderService = Depends(get_service),
    current_user: User = Depends(get_current_user)
):
    try:
        service.refund_order(
            order_id,
            current_user.user_id
        )

        return {"message": "Refund successful"}

    except OrderNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    except OrderAccessDeniedError:
        raise HTTPException(
            status_code=403,
            detail="Forbidden"
        )

    except InvalidOrderStatusError:
        raise HTTPException(
            status_code=400,
            detail="Order cannot be refunded"
        )

    except PaymentNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    except ProductNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )