from typing import Sequence, Tuple
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.sales import Order
from src.models.crm import Client
from src.models.enums import OrderStatusEnum


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_client_orders(self, client_id: int) -> Sequence[Order]:
        """Запрос 2: Заказы конкретного клиента с подгрузкой менеджера"""
        stmt = (
            select(Order)
            .options(joinedload(Order.employee))
            .where(Order.clientid == client_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_new_orders_queue(self) -> Sequence[Tuple[Order, str]]:
        """Запрос 13: Очередь новых заказов (возвращает Заказ и Имя клиента)"""
        stmt = (
            select(Order, Client.clientname)
            .join(Client, Order.clientid == Client.clientid)
            .where(Order.status == OrderStatusEnum.NEW)
            .order_by(Order.orderdate.asc())
        )
        result = await self.session.execute(stmt)
        # Возвращает список кортежей: [(OrderObj, "ООО Ромашка"), ...]
        return result.all()