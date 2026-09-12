from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class UserDB(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    name: Mapped[str] = mapped_column(String)

    orders: Mapped[list["OrderDB"]] = relationship(
    back_populates="user"
    )

    email: Mapped[str] = mapped_column(String, unique = True)
    password_hash: Mapped[str] = mapped_column(String)

class OrderDB(Base):
    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(
        Integer,
        primary_key = True
    )

    user_id: Mapped[int] = mapped_column(   
    Integer,
    ForeignKey("users.user_id")
    )

    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("products.product_id")
    )
    price: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String)

    user: Mapped["UserDB"] = relationship(
        back_populates="orders"
    )
    product: Mapped[list["ProductDB"]] = relationship(
         back_populates = "orders"
    )



class ProductDB(Base):
    __tablename__ = "products"

    product_id: Mapped[int] = mapped_column(
        Integer,
        primary_key = True
    )
    name: Mapped[str] = mapped_column(String)
    price: Mapped[int] = mapped_column(Integer)
    stock : Mapped[int] = mapped_column(Integer)


    orders: Mapped[list["OrderDB"]] = relationship(
        back_populates = "product"
    )

class PaymentDB(Base):
    __tablename__ = "payments"

    payment_id: Mapped[int] = mapped_column(
        Integer,
        primary_key = True
    )
    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("orders.order_id")
    )
    amount: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String)