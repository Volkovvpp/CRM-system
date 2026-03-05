from .base import Base
from .enums import (
    GenderEnum, OrderStatusEnum, ClientTypeEnum,
    InteractionTypeEnum, EmployeeStatusEnum, ClientStatusEnum
)
from .reference import Location, Employee, Product
from .crm import Client, Contact, Interaction
from .sales import Order, OrderItem

# Экспортируем все для удобного доступа из других частей приложения
__all__ = [
    "Base",
    "GenderEnum", "OrderStatusEnum", "ClientTypeEnum",
    "InteractionTypeEnum", "EmployeeStatusEnum", "ClientStatusEnum",
    "Location", "Employee", "Product",
    "Client", "Contact", "Interaction",
    "Order", "OrderItem"
]