from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr

from src.models.enums import ClientTypeEnum, ClientStatusEnum, GenderEnum, InteractionTypeEnum
from src.schemas.reference import LocationResponse, EmployeeResponse
from src.schemas.sales import OrderResponse


# ================= CONTACTS =================
class ContactBase(BaseModel):
    fullname: str
    position: Optional[str] = None
    workphone: Optional[str] = None
    mobilephone: Optional[str] = None
    email: Optional[EmailStr] = None

class ContactCreate(ContactBase):
    clientid: int

class ContactResponse(ContactBase):
    contactid: int
    model_config = ConfigDict(from_attributes=True)


# ================= INTERACTIONS =================
class InteractionBase(BaseModel):
    interactiontype: InteractionTypeEnum
    notes: Optional[str] = None

class InteractionCreate(InteractionBase):
    clientid: int
    employeeid: Optional[int] = None

class InteractionResponse(InteractionBase):
    interactionid: int
    interactiondate: datetime
    employee: Optional[EmployeeResponse] = None # Кто проводил взаимодействие
    model_config = ConfigDict(from_attributes=True)


# ================= CLIENTS =================
class ClientBase(BaseModel):
    clientname: str
    clienttype: ClientTypeEnum
    status: ClientStatusEnum = ClientStatusEnum.LEAD
    gender: Optional[GenderEnum] = None
    birthdate: Optional[date] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

class ClientCreate(ClientBase):
    locationid: Optional[int] = None
    responsibleemployeeid: Optional[int] = None

# Краткий ответ для списков (без тяжелых вложенностей)
class ClientResponseShort(ClientBase):
    clientid: int
    registrationdate: datetime
    location: Optional[LocationResponse] = None
    model_config = ConfigDict(from_attributes=True)

# ПОЛНАЯ КАРТОЧКА КЛИЕНТА (Под ваш запрос №1 из БД)
class ClientResponseFull(ClientResponseShort):
    responsible_employee: Optional[EmployeeResponse] = None
    contacts: List[ContactResponse] = []
    interactions: List[InteractionResponse] = []
    orders: List[OrderResponse] = []