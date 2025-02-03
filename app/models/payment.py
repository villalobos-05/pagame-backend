from datetime import datetime
from enum import Enum
from pydantic import BaseModel, constr


class PaymentStatus(str, Enum):
    UNPAYED = "unpayed"
    PAYED = "payed"
    UNCHECKED = "uncheked"
    REJECTED = "rejected"


class Payment(BaseModel):
    id: str
    payerId: str
    receiverId: str
    money: float
    issue: str
    status: PaymentStatus
    createdAt: datetime
    checkedAt: datetime | None = None


class CreatePayment(BaseModel):
    payerId: str
    money: float
    issue: constr(max_length=42)  # type: ignore
