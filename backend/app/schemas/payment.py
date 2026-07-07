from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class PaymentCreateIn(BaseModel):
    order_id: int
    pay_channel: str = Field(default="mock", max_length=32)


class PaymentOut(ORMModel):
    id: int
    payment_no: str
    order_id: int
    order_no: str
    user_id: int
    pay_amount_cent: int
    pay_channel: str
    status: str
    paid_at: datetime | None
    third_party_trade_no: str | None
    created_at: datetime
    updated_at: datetime


class PaymentCreateOut(PaymentOut):
    pay_url: str | None = None
