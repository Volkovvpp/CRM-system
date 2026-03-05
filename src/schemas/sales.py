from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from src.models.enums import OrderStatusEnum
from src.schemas.reference import ProductResponse, EmployeeResponse


# ================= ORDER ITEMS =================
class OrderItemBase(BaseModel):
    productid: int
    quantity: int
    priceperitem: Decimal


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    orderitemid: int
    # Вложенный товар (чтобы при просмотре заказа было видно название товара)
    product: Optional[ProductResponse] = None
    model_config = ConfigDict(from_attributes=True)


# ================= ORDERS =================
class OrderBase(BaseModel):
    clientid: int
    employeeid: Optional[int] = None
    status: OrderStatusEnum = OrderStatusEnum.NEW
    totalamount: Optional[Decimal] = Decimal('0.00')


class OrderCreate(OrderBase):
    # При создании заказа удобно сразу передавать список товаров
    items: List[OrderItemCreate] = []


class OrderResponse(OrderBase):
    orderid: int
    orderdate: datetime

    # Вложенные данные (для Детализации заказа)
    items: List[OrderItemResponse] = []
    employee: Optional[EmployeeResponse] = None

    model_config = ConfigDict(from_attributes=True)