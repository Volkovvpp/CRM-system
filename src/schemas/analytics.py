from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


# Запрос 5: Рейтинг
class ManagerRatingResponse(BaseModel):
    fullname: str
    interactions_count: int

# Запрос 12: Топ по количеству
class TopProductQtyResponse(BaseModel):
    productname: str
    total_qty: int

# Запрос 18: Топ по выручке
class TopProductRevResponse(BaseModel):
    productname: str
    revenue: Decimal

# Запрос 17: Любимые товары
class FavoriteProductResponse(BaseModel):
    clientid: int
    productname: str
    purchases_count: int

# Запрос 21: ABC Анализ
class ABCAnalysisResponse(BaseModel):
    ClientID: int
    ClientName: str
    ClientRevenue: Decimal
    CumulativePercent: Decimal
    ABC_Category: str

# Запрос 22: XYZ Анализ
class XYZAnalysisResponse(BaseModel):
    ClientID: int
    ClientName: str
    AvgRev: Decimal
    StdRev: Decimal
    CoefficientVariation: Optional[Decimal]
    XYZ_Category: str

# Запрос 23: RFM Анализ
class RFMAnalysisResponse(BaseModel):
    ClientID: int
    ClientName: str
    Recency: int
    Frequency: int
    Monetary: Decimal
    R_Score: int
    F_Score: int
    M_Score: int
    Segment: str