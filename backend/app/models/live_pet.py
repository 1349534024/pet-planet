from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class LivePet(Base, TimestampMixin):
    __tablename__ = "live_pet"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    merchant_id: Mapped[int] = mapped_column(ForeignKey("merchant.id"), index=True)
    publisher_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    name: Mapped[str] = mapped_column(String(64))
    type: Mapped[str] = mapped_column(String(32), index=True)
    breed: Mapped[str | None] = mapped_column(String(64))
    gender: Mapped[str] = mapped_column(String(16), default="unknown")
    birthday: Mapped[date | None] = mapped_column(Date)
    color: Mapped[str | None] = mapped_column(String(64))
    weight: Mapped[str | None] = mapped_column(String(32))
    city: Mapped[str | None] = mapped_column(String(64), index=True)
    price_cent: Mapped[int] = mapped_column(Integer, default=0)
    deposit_cent: Mapped[int] = mapped_column(Integer, default=0)
    vaccine_status: Mapped[str] = mapped_column(String(32), default="unknown")
    deworm_status: Mapped[str] = mapped_column(String(32), default="unknown")
    health_desc: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    support_video_view: Mapped[str] = mapped_column(String(16), default="no")
    support_offline_view: Mapped[str] = mapped_column(String(16), default="no")
    audit_status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    audit_reason: Mapped[str | None] = mapped_column(String(255))
    audited_by: Mapped[int | None] = mapped_column(ForeignKey("user.id"), index=True)
    audited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(32), default="draft")


class LivePetMedia(Base, TimestampMixin):
    __tablename__ = "live_pet_media"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    live_pet_id: Mapped[int] = mapped_column(ForeignKey("live_pet.id"), index=True)
    file_asset_id: Mapped[int | None] = mapped_column(ForeignKey("file_asset.id"), index=True)
    media_type: Mapped[str] = mapped_column(String(32), index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="active")


class LivePetCertificate(Base, TimestampMixin):
    __tablename__ = "live_pet_certificate"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    live_pet_id: Mapped[int] = mapped_column(ForeignKey("live_pet.id"), index=True)
    certificate_type: Mapped[str] = mapped_column(String(64), index=True)
    file_asset_id: Mapped[int | None] = mapped_column(ForeignKey("file_asset.id"), index=True)
    certificate_no: Mapped[str | None] = mapped_column(String(128))
    issued_at: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(32), default="active")

