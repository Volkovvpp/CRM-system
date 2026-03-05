from datetime import datetime, timedelta
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.crm import Client, Contact
from src.models.reference import Location
from src.models.sales import Order
from src.models.enums import ClientTypeEnum, ClientStatusEnum, GenderEnum


class ClientRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_client_card_full(self, client_id: int) -> Client | None:
        """
        Запрос 1: Полная карточка клиента со всеми связями (аналог большого LEFT JOIN).
        Используем selectinload/joinedload для избежания N+1 проблемы.
        """
        stmt = (
            select(Client)
            .options(
                joinedload(Client.location),
                joinedload(Client.responsible_employee),
                selectinload(Client.contacts),
                selectinload(Client.orders).joinedload(Order.items),
                selectinload(Client.interactions).joinedload(Interaction.employee)
            )
            .where(Client.clientid == client_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_contacts_by_client(self, client_id: int) -> Sequence[Contact]:
        """Запрос 3: Найти контактное лицо по ID клиента"""
        stmt = select(Contact).where(Contact.clientid == client_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_clients_by_manager(self, manager_id: int) -> Sequence[Client]:
        """Запрос 4: Показать всех клиентов конкретного менеджера"""
        stmt = select(Client).where(Client.responsibleemployeeid == manager_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_b2c_clients(self) -> Sequence[Client]:
        """Запрос 6: Физ. лица"""
        stmt = select(Client).where(Client.clienttype == ClientTypeEnum.B2C)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_dormant_clients(self) -> Sequence[Client]:
        """Запрос 7: Спящие клиенты (нет заказов последние 36 месяцев)"""
        thirty_six_months_ago = datetime.now() - timedelta(days=36*30)
        stmt = (
            select(Client)
            .join(Order, Order.clientid == Client.clientid)
            .where(Order.orderdate <= thirty_six_months_ago)
            .distinct()
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_new_clients_last_30_days(self) -> Sequence[Client]:
        """Запрос 8: Клиенты за последние 30 дней"""
        thirty_days_ago = datetime.now() - timedelta(days=30)
        stmt = select(Client).where(Client.registrationdate >= thirty_days_ago)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_leads(self) -> Sequence[Client]:
        """Запрос 9: Только Лиды"""
        stmt = select(Client).where(Client.status == ClientStatusEnum.LEAD)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_target_b2c_female(self) -> Sequence[Client]:
        """Запрос 10: Женщины > 30 лет (упрощенный расчет возраста через дату)"""
        thirty_years_ago = datetime.now().date() - timedelta(days=30*365)
        stmt = (
            select(Client)
            .where(
                Client.clienttype == ClientTypeEnum.B2C,
                Client.gender == GenderEnum.F,
                Client.birthdate < thirty_years_ago
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_clients_by_geo(self, country: str, city: str) -> Sequence[Client]:
        """Запрос 11: Клиенты по геолокации"""
        stmt = (
            select(Client)
            .join(Location, Client.locationid == Location.locationid)
            .where(Location.country == country, Location.city == city)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()