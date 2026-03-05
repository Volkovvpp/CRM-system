import enum

class GenderEnum(str, enum.Enum):
    M = 'М'
    F = 'Ж'

class OrderStatusEnum(str, enum.Enum):
    NEW = 'Новый'
    IN_PROGRESS = 'В обработке'
    COMPLETED = 'Выполнен'
    CANCELED = 'Отменен'

class ClientTypeEnum(str, enum.Enum):
    B2B = 'Юр. лицо'
    B2C = 'Физ. лицо'

class InteractionTypeEnum(str, enum.Enum):
    CALL = 'Звонок'
    MEETING = 'Встреча'
    EMAIL = 'Email'
    OTHER = 'Другое'

class EmployeeStatusEnum(str, enum.Enum):
    ACTIVE = 'Активен'
    FIRED = 'Уволен'
    VACATION = 'В отпуске'

class ClientStatusEnum(str, enum.Enum):
    LEAD = 'Лид'
    ACTIVE = 'Активный'
    LOST = 'Потерянный'
    VIP = 'VIP'