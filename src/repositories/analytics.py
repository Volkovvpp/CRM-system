from typing import Sequence, Any
from sqlalchemy import select, func, desc, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.reference import Employee, Product
from src.models.crm import Interaction, Client
from src.models.sales import OrderItem, Order


class AnalyticsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_manager_rating(self) -> Sequence[Any]:
        """Запрос 5: Рейтинг менеджеров по кол-ву взаимодействий"""
        stmt = (
            select(Employee.fullname, func.count(Interaction.interactionid).label('interactions_count'))
            .join(Interaction, Employee.employeeid == Interaction.employeeid)
            .group_by(Employee.fullname)
            .order_by(desc('interactions_count'))
        )
        result = await self.session.execute(stmt)
        return result.all()

    async def get_top_products_by_quantity(self, limit: int = 10) -> Sequence[Any]:
        """Запрос 12: Самые продаваемые товары по количеству"""
        stmt = (
            select(Product.productname, func.sum(OrderItem.quantity).label('total_qty'))
            .join(OrderItem, Product.productid == OrderItem.productid)
            .group_by(Product.productname)
            .order_by(desc('total_qty'))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.all()

    async def get_top_products_by_revenue(self, limit: int = 10) -> Sequence[Any]:
        """Запрос 18: Самые прибыльные товары по выручке"""
        stmt = (
            select(Product.productname, func.sum(OrderItem.quantity * OrderItem.priceperitem).label('revenue'))
            .join(OrderItem, Product.productid == OrderItem.productid)
            .group_by(Product.productname)
            .order_by(desc('revenue'))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.all()

    async def get_favorite_products_per_client(self) -> Sequence[Any]:
        """Запрос 17: Любимые товары по клиентам"""
        stmt = (
            select(Client.clientid, Product.productname, func.count('*').label('purchases_count'))
            .join(Order, Client.clientid == Order.clientid)
            .join(OrderItem, Order.orderid == OrderItem.orderid)
            .join(Product, OrderItem.productid == Product.productid)
            .group_by(Client.clientid, Product.productname)
            .order_by(Client.clientid, desc('purchases_count'))
        )
        result = await self.session.execute(stmt)
        return result.all()

    async def run_abc_analysis(self) -> Sequence[Any]:
        """Запрос 21: ABC-Анализ"""
        query = text("""
            WITH TotalRevenue AS (
                SELECT o.ClientID, SUM(o.TotalAmount) AS ClientRevenue
                FROM Orders o GROUP BY o.ClientID
            ),
            SortedRevenue AS (
                SELECT tr.ClientID, tr.ClientRevenue,
                       tr.ClientRevenue / (SELECT SUM(ClientRevenue) FROM TotalRevenue) AS RevenueShare
                FROM TotalRevenue tr
            ),
            Cumulative AS (
                SELECT ClientID, ClientRevenue, RevenueShare,
                       SUM(RevenueShare) OVER (ORDER BY ClientRevenue DESC) AS CumShare
                FROM SortedRevenue
            )
            SELECT c.ClientID, cl.ClientName, c.ClientRevenue,
                   ROUND(c.CumShare * 100, 2) AS CumulativePercent,
                   CASE WHEN c.CumShare <= 0.8 THEN 'A'
                        WHEN c.CumShare <= 0.95 THEN 'B' ELSE 'C' END AS ABC_Category
            FROM Cumulative c
            JOIN Clients cl ON cl.ClientID = c.ClientID
            ORDER BY c.ClientRevenue DESC;
        """)
        result = await self.session.execute(query)
        return result.mappings().all()

    async def run_xyz_analysis(self) -> Sequence[Any]:
        """Запрос 22: XYZ-Анализ"""
        query = text("""
            WITH MonthlyStats AS (
                SELECT o.ClientID, DATE_TRUNC('month', o.OrderDate) AS Month, SUM(o.TotalAmount) AS MonthlyRevenue
                FROM Orders o GROUP BY o.ClientID, DATE_TRUNC('month', o.OrderDate)
            ),
            Stats AS (
                SELECT ClientID, AVG(MonthlyRevenue) AS AvgRev, STDDEV(MonthlyRevenue) AS StdRev
                FROM MonthlyStats GROUP BY ClientID
            ),
            Variation AS (
                SELECT ClientID, AvgRev, StdRev,
                       CASE WHEN AvgRev = 0 THEN NULL ELSE StdRev / AvgRev END AS CV
                FROM Stats
            )
            SELECT v.ClientID, c.ClientName, v.AvgRev, v.StdRev, ROUND(v.CV, 3) AS CoefficientVariation,
                   CASE WHEN v.CV IS NULL THEN 'Z'
                        WHEN v.CV <= 0.1 THEN 'X'
                        WHEN v.CV <= 0.25 THEN 'Y' ELSE 'Z' END AS XYZ_Category
            FROM Variation v
            JOIN Clients c ON c.ClientID = v.ClientID
            ORDER BY v.CV NULLS LAST;
        """)
        result = await self.session.execute(query)
        return result.mappings().all()

    async def run_rfm_analysis(self) -> Sequence[Any]:
        """Запрос 23: Полный RFM-Анализ с сегментацией"""
        query = text("""
                     WITH RFM AS (SELECT c.ClientID,
                                         c.ClientName,
                                         -- Recency: количество дней с момента последнего заказа
                                         COALESCE(DATE_PART('day', NOW() - MAX(o.OrderDate)), 9999) AS Recency,
                                         -- Frequency: количество заказов
                                         COUNT(o.OrderID)                                           AS Frequency,
                                         -- Monetary: сумма всех заказов клиента
                                         COALESCE(SUM(o.TotalAmount), 0)                            AS Monetary
                                  FROM Clients c
                                           LEFT JOIN Orders o ON o.ClientID = c.ClientID
                                  GROUP BY c.ClientID),
                          RFMScores AS (SELECT *,
                                               -- R (давность)
                                               CASE
                                                   WHEN Recency <= 30 THEN 3
                                                   WHEN Recency <= 90 THEN 2
                                                   ELSE 1
                                                   END AS R_Score,
                                               -- F (частота)
                                               CASE
                                                   WHEN Frequency >= 5 THEN 3
                                                   WHEN Frequency >= 2 THEN 2
                                                   ELSE 1
                                                   END AS F_Score,
                                               -- M (деньги)
                                               CASE
                                                   WHEN Monetary >= 20000 THEN 3
                                                   WHEN Monetary >= 5000 THEN 2
                                                   ELSE 1
                                                   END AS M_Score
                                        FROM RFM)
                     SELECT ClientID,
                            ClientName,
                            Recency,
                            Frequency,
                            Monetary,
                            R_Score,
                            F_Score,
                            M_Score,

                            CASE
                                WHEN R_Score = 3 AND F_Score = 3 AND M_Score = 3
                                    THEN 'Активный клиент'
                                WHEN R_Score >= 2 AND F_Score >= 2 AND M_Score >= 2
                                    THEN 'Перспективный клиент'
                                WHEN F_Score = 1 AND Monetary < 3000 AND R_Score = 3
                                    THEN 'Новичок'
                                WHEN F_Score = 1 AND R_Score = 2
                                    THEN 'Редко покупает'
                                WHEN R_Score = 1
                                    THEN 'Потерял интерес'
                                ELSE 'Неопределённый сегмент'
                                END AS Segment
                     FROM RFMScores
                     ORDER BY Segment, ClientID;
                     """)
        result = await self.session.execute(query)
        return result.mappings().all()