from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.order import MallOrder


class PaymentOrder(Base, TimestampMixin):
    __tablename__ = "payment_order"
    __table_args__ = (
        UniqueConstraint("payment_no", name="uq_payment_order_no"),
        UniqueConstraint("user_id", "idempotency_key", name="uq_payment_order_user_idempotency"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    payment_no: Mapped[str] = mapped_column(String(64), index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("mall_order.id"), index=True)
    order_no: Mapped[str] = mapped_column(String(64), index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    pay_amount_cent: Mapped[int] = mapped_column(Integer)
    pay_channel: Mapped[str] = mapped_column(String(32), default="mock", index=True)
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    third_party_trade_no: Mapped[str | None] = mapped_column(String(128), index=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(128), index=True)

    order: Mapped[MallOrder] = relationship(lazy="selectin")
