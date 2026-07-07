from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class ServiceItem(Base, TimestampMixin):
    __tablename__ = "service_item"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    merchant_id: Mapped[int] = mapped_column(ForeignKey("merchant.id"), index=True)
    store_id: Mapped[int | None] = mapped_column(ForeignKey("merchant_store.id"), index=True)
    name: Mapped[str] = mapped_column(String(128), index=True)
    service_type: Mapped[str] = mapped_column(String(32), index=True)
    price_cent: Mapped[int] = mapped_column(Integer, default=0)
    duration_minutes: Mapped[int | None] = mapped_column(Integer)
    applicable_pet_type: Mapped[str | None] = mapped_column(String(64))
    description: Mapped[str | None] = mapped_column(Text)
    refund_rule: Mapped[str | None] = mapped_column(Text)
    audit_status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    audit_reason: Mapped[str | None] = mapped_column(String(255))
    audited_by: Mapped[int | None] = mapped_column(ForeignKey("user.id"), index=True)
    audited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(32), default="active")


class ServiceSchedule(Base, TimestampMixin):
    __tablename__ = "service_schedule"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    service_item_id: Mapped[int] = mapped_column(ForeignKey("service_item.id"), index=True)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    capacity: Mapped[int] = mapped_column(Integer, default=1)
    booked_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="available")


class ServiceBooking(Base, TimestampMixin):
    __tablename__ = "service_booking"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    pet_id: Mapped[int | None] = mapped_column(ForeignKey("pet_profile.id"), index=True)
    service_item_id: Mapped[int] = mapped_column(ForeignKey("service_item.id"), index=True)
    schedule_id: Mapped[int | None] = mapped_column(ForeignKey("service_schedule.id"), index=True)
    contact_name: Mapped[str] = mapped_column(String(64))
    contact_phone: Mapped[str] = mapped_column(String(32))
    remark: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="submitted", index=True)


class ServiceReport(Base, TimestampMixin):
    __tablename__ = "service_report"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("service_booking.id"), index=True)
    reporter_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    content: Mapped[str | None] = mapped_column(Text)
    before_media_asset_ids: Mapped[str | None] = mapped_column(String(512))
    during_media_asset_ids: Mapped[str | None] = mapped_column(String(512))
    after_media_asset_ids: Mapped[str | None] = mapped_column(String(512))
    abnormal_note: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="submitted")
