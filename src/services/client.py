from sqlalchemy.ext.asyncio import AsyncSession
from src.models.crm import Client
from src.schemas.crm import ClientCreate
from src.models.enums import ClientTypeEnum
from src.repositories.client import ClientRepository


class ClientService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ClientRepository(session)

    async def create_client(self, client_in: ClientCreate) -> Client:
        """Создание клиента с валидацией бизнес-правил B2B/B2C"""

        # БИЗНЕС-ПРАВИЛО (Дублируем CHECK constraint из БД для красивой отдачи ошибки)
        if client_in.clienttype == ClientTypeEnum.B2B:
            if client_in.gender is not None or client_in.birthdate is not None:
                raise ValueError("Для Юр. лица нельзя указывать Пол и Дату рождения!")

        elif client_in.clienttype == ClientTypeEnum.B2C:
            if client_in.gender is None or client_in.birthdate is None:
                raise ValueError("Для Физ. лица Пол и Дата рождения обязательны!")

        # Создаем модель
        new_client = Client(
            clientname=client_in.clientname,
            clienttype=client_in.clienttype,
            status=client_in.status,
            gender=client_in.gender,
            birthdate=client_in.birthdate,
            phone=client_in.phone,
            email=client_in.email,
            locationid=client_in.locationid,
            responsibleemployeeid=client_in.responsibleemployeeid
        )

        self.session.add(new_client)
        await self.session.commit()
        await self.session.refresh(new_client)

        return new_client

    async def get_full_client_info(self, client_id: int):
        """Просто проксируем вызов к репозиторию"""
        client = await self.repo.get_client_card_full(client_id)
        if not client:
            raise ValueError("Клиент не найден")
        return client