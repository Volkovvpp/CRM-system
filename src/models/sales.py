from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import Integer, Numeric, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base
from .enums import OrderStatusEnum


class Order(Base):
    __tablename__ = 'orders'

    orderid: Mapped[int] = mapped_column(primary_key=True)
    clientid: Mapped[int] = mapped_column(ForeignKey('clients.clientid', ondelete='CASCADE'))
    employeeid: Mapped[Optional[int]] = mapped_column(ForeignKey('employees.employeeid', ondelete='RESTRICT'))
    orderdate: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[OrderStatusEnum] = mapped_column(
        SQLEnum(OrderStatusEnum, name="order_status_enum", create_type=False),
        default=OrderStatusEnum.NEW
    )
    totalamount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), default=0.00)

    client: Mapped["Client"] = relationship(back_populates="orders")
    employee: Mapped[Optional["Employee"]] = relationship(back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(back_populates="order", cascade="all, delete")


class OrderItem(Base):
    __tablename__ = 'order_items'

    orderitemid: Mapped[int] = mapped_column(primary_key=True)
    orderid: Mapped[int] = mapped_column(ForeignKey('orders.orderid', ondelete='CASCADE'))
    productid: Mapped[int] = mapped_column(ForeignKey('products.productid', ondelete='RESTRICT'))
    quantity: Mapped[int] = mapped_column(Integer)
    priceperitem: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")