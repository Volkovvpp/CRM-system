from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.reference import Employee
from src.schemas.reference import EmployeeCreate
from src.services.auth import AuthService


class EmployeeService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_employee(self, employee_in: EmployeeCreate) -> Employee:
        """Регистрация нового сотрудника с безопасным сохранением пароля"""

        # 1. Проверяем, нет ли уже такого Email (Бизнес-правило)
        stmt = select(Employee).where(Employee.email == employee_in.email)
        result = await self.session.execute(stmt)
        if result.scalars().first():
            raise ValueError("Сотрудник с таким Email уже существует!")

        # 2. Хэшируем пароль!
        hashed_pw = AuthService.get_password_hash(employee_in.password)

        # 3. Создаем ORM модель
        new_employee = Employee(
            fullname=employee_in.fullname,
            position=employee_in.position,
            email=str(employee_in.email),
            passwordhash=hashed_pw,  # <- Сохраняем ХЭШ, а не открытый пароль
            status=employee_in.status
        )

        # 4. Сохраняем в БД
        self.session.add(new_employee)
        await self.session.commit()
        await self.session.refresh(new_employee)

        return new_employee