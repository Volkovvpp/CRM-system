from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr

from src.models.enums import EmployeeStatusEnum


# ================= LOCATIONS =================
class LocationBase(BaseModel):
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None

class LocationCreate(LocationBase):
    pass

class LocationResponse(LocationBase):
    locationid: int
    model_config = ConfigDict(from_attributes=True)


# ================= PRODUCTS =================
class ProductBase(BaseModel):
    productname: str
    description: Optional[str] = None
    price: Decimal
    isservice: bool = False

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    productid: int
    createdat: datetime
    model_config = ConfigDict(from_attributes=True)


# ================= EMPLOYEES =================
class EmployeeBase(BaseModel):
    fullname: str
    position: Optional[str] = None
    email: EmailStr
    status: EmployeeStatusEnum = EmployeeStatusEnum.ACTIVE

class EmployeeCreate(EmployeeBase):
    password: str # Принимаем пароль текстом, хэшировать будем в Service слое!

class EmployeeResponse(EmployeeBase):
    employeeid: int
    hiredate: datetime
    # ПАРОЛЬ СЮДА НЕ ДОБАВЛЯЕМ! Безопасность данных.
    model_config = ConfigDict(from_attributes=True)