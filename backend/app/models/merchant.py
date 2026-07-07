from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Merchant(Base, TimestampMixin):
    __tablename__ = "merchant"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    merchant_type: Mapped[str] = mapped_column(String(32), index=True)
    name: Mapped[str] = mapped_column(String(128), index=True)
    contact_name: Mapped[str] = mapped_column(String(64))
    contact_phone: Mapped[str] = mapped_column(String(32))
    city: Mapped[str | None] = mapped_column(String(64))
    address: Mapped[str | None] = mapped_column(String(255))
    business_scope: Mapped[str | None] = mapped_column(String(255))
    settlement_account: Mapped[str | None] = mapped_column(String(255))
    deposit_status: Mapped[str] = mapped_column(String(32), default="unpaid")
    audit_status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    audit_reason: Mapped[str | None] = mapped_column(String(255))
    audited_by: Mapped[int | None] = mapped_column(ForeignKey("user.id"), index=True)
    audited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(32), default="active")


class MerchantQualification(Base, TimestampMixin):
    __tablename__ = "merchant_qualification"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    merchant_id: Mapped[int] = mapped_column(ForeignKey("merchant.id"), index=True)
    qualification_type: Mapped[str] = mapped_column(String(64), index=True)
    file_asset_id: Mapped[int | None] = mapped_column(ForeignKey("file_asset.id"), index=True)
    certificate_no: Mapped[str | None] = mapped_column(String(128))
    description: Mapped[str | None] = mapped_column(Text)
    audit_status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    audit_reason: Mapped[str | None] = mapped_column(String(255))
    audited_by: Mapped[int | None] = mapped_column(ForeignKey("user.id"), index=True)
    audited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(32), default="active")


class MerchantStore(Base, TimestampMixin):
    __tablename__ = "merchant_store"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    merchant_id: Mapped[int] = mapped_column(ForeignKey("merchant.id"), index=True)
    name: Mapped[str] = mapped_column(String(128))
    province: Mapped[str | None] = mapped_column(String(64))
    city: Mapped[str | None] = mapped_column(String(64))
    district: Mapped[str | None] = mapped_column(String(64))
    address: Mapped[str] = mapped_column(String(255))
    contact_phone: Mapped[str | None] = mapped_column(String(32))
    cover_file_asset_id: Mapped[int | None] = mapped_column(ForeignKey("file_asset.id"), index=True)
    longitude: Mapped[str | None] = mapped_column(String(32))
    latitude: Mapped[str | None] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), default="active")
