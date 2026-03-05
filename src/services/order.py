from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.sales import Order, OrderItem
from src.models.reference import Product
from src.schemas.sales import OrderCreate


class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_order_with_items(self, order_in: OrderCreate) -> Order:
        """
        Комплексное создание заказа:
        1. Создает "шапку" заказа.
        2. Проверяет реальные цены товаров.
        3. Высчитывает TotalAmount.
        4. Сохраняет всё в одной транзакции.
        """
        total_amount = Decimal('0.00')
        order_items_orm = []

        # 1. Проходим по всем товарам, которые прислали в DTO
        for item_in in order_in.items:
            # БИЗНЕС-ЛОГИКА: Достаем реальный товар из базы, чтобы узнать его ЦЕНУ
            stmt = select(Product).where(Product.productid == item_in.productid)
            result = await self.session.execute(stmt)
            real_product = result.scalars().first()

            if not real_product:
                raise ValueError(f"Товар с ID {item_in.productid} не найден!")

            # Высчитываем стоимость позиции (Реальная цена из БД * Количество)
            item_total = real_product.price * item_in.quantity
            total_amount += item_total

            # Создаем ORM позицию заказа
            order_items_orm.append(
                OrderItem(
                    productid=real_product.productid,
                    quantity=item_in.quantity,
                    priceperitem=real_product.price # Записываем реальную цену на момент продажи
                )
            )

        # 2. Создаем сам Заказ
        new_order = Order(
            clientid=order_in.clientid,
            employeeid=order_in.employeeid,
            status=order_in.status,
            totalamount=total_amount, # Устанавливаем рассчитанную нами сумму!
            order_items=order_items_orm # Передаем список позиций (SQLAlchemy свяжет их сама)
        )

        # 3. Сохраняем в базу (ТРАНЗАКЦИЯ)
        # Если здесь произойдет ошибка, ни заказ, ни товары не сохранятся
        self.session.add(new_order)
        await self.session.commit()
        await self.session.refresh(new_order)

        return new_order