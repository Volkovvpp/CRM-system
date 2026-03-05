from datetime import datetime
from decimal import Decimal
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import String, Text, Boolean, DateTime, Numeric, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base
from .enums import EmployeeStatusEnum

if TYPE_CHECKING:
    from .crm import Client, Interaction
    from .sales import Order, OrderItem


class Location(Base):
    __tablename__ = 'locations'

    locationid: Mapped[int] = mapped_column(primary_key=True)
    city: Mapped[Optional[str]] = mapped_column(String(100))
    region: Mapped[Optional[str]] = mapped_column(String(100))
    country: Mapped[Optional[str]] = mapped_column(String(100))

    # Строковое указание "Client" спасает от циклических импортов
    clients: Mapped[List["Client"]] = relationship(back_populates="location")


class Employee(Base):
    __tablename__ = 'employees'

    employeeid: Mapped[int] = mapped_column(primary_key=True)
    fullname: Mapped[str] = mapped_column(String(255))
    position: Mapped[Optional[str]] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    passwordhash: Mapped[str] = mapped_column(String(255))
    hiredate: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[EmployeeStatusEnum] = mapped_column(
        SQLEnum(EmployeeStatusEnum, name="employee_status_enum", create_type=False),
        default=EmployeeStatusEnum.ACTIVE
    )

    clients: Mapped[List["Client"]] = relationship(back_populates="responsible_employee")
    orders: Mapped[List["Order"]] = relationship(back_populates="employee")
    interactions: Mapped[List["Interaction"]] = relationship(back_populates="employee")


class Product(Base):
    __tablename__ = 'products'

    productid: Mapped[int] = mapped_column(primary_key=True)
    productname: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    isservice: Mapped[bool] = mapped_column(Boolean, default=False)
    createdat: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="product")