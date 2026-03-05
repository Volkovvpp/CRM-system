from datetime import date, datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import String, Date, DateTime, Text, ForeignKey, CheckConstraint, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base
from .enums import ClientTypeEnum, ClientStatusEnum, GenderEnum, InteractionTypeEnum

if TYPE_CHECKING:
    from .reference import Location, Employee
    from .sales import Order


class Client(Base):
    __tablename__ = 'clients'
    __table_args__ = (
        CheckConstraint(
            "(clienttype = 'Физ. лицо') OR (clienttype = 'Юр. лицо' AND gender IS NULL AND birthdate IS NULL)",
            name='chk_b2b_personal_data'
        ),
    )

    clientid: Mapped[int] = mapped_column(primary_key=True)
    clientname: Mapped[str] = mapped_column(String(255))
    clienttype: Mapped[ClientTypeEnum] = mapped_column(
        SQLEnum(ClientTypeEnum, name="client_type_enum", create_type=False))
    status: Mapped[ClientStatusEnum] = mapped_column(
        SQLEnum(ClientStatusEnum, name="client_status_enum", create_type=False),
        default=ClientStatusEnum.LEAD
    )
    gender: Mapped[Optional[GenderEnum]] = mapped_column(SQLEnum(GenderEnum, name="gender_enum", create_type=False))
    birthdate: Mapped[Optional[date]] = mapped_column(Date)
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    registrationdate: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    locationid: Mapped[Optional[int]] = mapped_column(ForeignKey('locations.locationid', ondelete='SET NULL'))
    responsibleemployeeid: Mapped[Optional[int]] = mapped_column(
        ForeignKey('employees.employeeid', ondelete='RESTRICT'))

    location: Mapped[Optional["Location"]] = relationship(back_populates="clients")
    responsible_employee: Mapped[Optional["Employee"]] = relationship(back_populates="clients")
    contacts: Mapped[List["Contact"]] = relationship(back_populates="client", cascade="all, delete")
    orders: Mapped[List["Order"]] = relationship(back_populates="client", cascade="all, delete")
    interactions: Mapped[List["Interaction"]] = relationship(back_populates="client", cascade="all, delete")


class Contact(Base):
    __tablename__ = 'contacts'

    contactid: Mapped[int] = mapped_column(primary_key=True)
    clientid: Mapped[int] = mapped_column(ForeignKey('clients.clientid', ondelete='CASCADE'))
    fullname: Mapped[str] = mapped_column(String(255))
    position: Mapped[Optional[str]] = mapped_column(String(100))
    workphone: Mapped[Optional[str]] = mapped_column(String(50))
    mobilephone: Mapped[Optional[str]] = mapped_column(String(50))
    email: Mapped[Optional[str]] = mapped_column(String(255))

    client: Mapped["Client"] = relationship(back_populates="contacts")


class Interaction(Base):
    __tablename__ = 'interactions'

    interactionid: Mapped[int] = mapped_column(primary_key=True)
    clientid: Mapped[int] = mapped_column(ForeignKey('clients.clientid', ondelete='CASCADE'))
    employeeid: Mapped[Optional[int]] = mapped_column(ForeignKey('employees.employeeid', ondelete='RESTRICT'))
    interactiontype: Mapped[InteractionTypeEnum] = mapped_column(
        SQLEnum(InteractionTypeEnum, name="interaction_type_enum", create_type=False))
    interactiondate: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    notes: Mapped[Optional[str]] = mapped_column(Text)

    client: Mapped["Client"] = relationship(back_populates="interactions")
    employee: Mapped[Optional["Employee"]] = relationship(back_populates="interactions")