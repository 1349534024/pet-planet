from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class MallOrder(Base, TimestampMixin):
    __tablename__ = "mall_order"
    __table_args__ = (
        UniqueConstraint("order_no", name="uq_mall_order_no"),
        UniqueConstraint("user_id", "idempotency_key", name="uq_mall_order_user_idempotency"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_no: Mapped[str] = mapped_column(String(64), index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    address_id: Mapped[int | None] = mapped_column(Integer, index=True)
    receiver_name: Mapped[str] = mapped_column(String(64))
    receiver_phone: Mapped[str] = mapped_column(String(32))
    province: Mapped[str] = mapped_column(String(64))
    city: Mapped[str] = mapped_column(String(64))
    district: Mapped[str] = mapped_column(String(64))
    detail: Mapped[str] = mapped_column(String(255))
    total_amount_cent: Mapped[int] = mapped_column(Integer, default=0)
    freight_amount_cent: Mapped[int] = mapped_column(Integer, default=0)
    discount_amount_cent: Mapped[int] = mapped_column(Integer, default=0)
    pay_amount_cent: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="pending_payment", index=True)
    payment_status: Mapped[str] = mapped_column(String(32), default="unpaid", index=True)
    tracking_company: Mapped[str | None] = mapped_column(String(64))
    tracking_no: Mapped[str | None] = mapped_column(String(128), index=True)
    shipped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    remark: Mapped[str | None] = mapped_column(Text)
    idempotency_key: Mapped[str | None] = mapped_column(String(128), index=True)

    items: Mapped[list["MallOrderItem"]] = relationship(back_populates="order", lazy="selectin")


class MallOrderItem(Base, TimestampMixin):
    __tablename__ = "mall_order_item"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("mall_order.id"), index=True)
    order_no: Mapped[str] = mapped_column(String(64), index=True)
    product_id: Mapped[int] = mapped_column(Integer, index=True)
    sku_id: Mapped[int] = mapped_column(Integer, index=True)
    merchant_id: Mapped[int | None] = mapped_column(Integer, index=True)
    product_title: Mapped[str] = mapped_column(String(255))
    product_main_image: Mapped[str | None] = mapped_column(String(512))
    sku_name: Mapped[str] = mapped_column(String(128))
    sku_specs: Mapped[str | None] = mapped_column(Text)
    unit_price_cent: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer)
    total_amount_cent: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)

    order: Mapped[MallOrder] = relationship(back_populates="items")
