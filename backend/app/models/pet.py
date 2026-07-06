from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class PetProfile(Base, TimestampMixin):
    __tablename__ = "pet_profile"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    name: Mapped[str] = mapped_column(String(64))
    type: Mapped[str] = mapped_column(String(32), index=True)
    breed: Mapped[str | None] = mapped_column(String(64))
    gender: Mapped[str] = mapped_column(String(16), default="unknown")
    birthday: Mapped[date | None] = mapped_column(Date)
    arrival_date: Mapped[date | None] = mapped_column(Date)
    weight: Mapped[str | None] = mapped_column(String(32))
    avatar: Mapped[str | None] = mapped_column(String(512))
    sterilized: Mapped[str] = mapped_column(String(16), default="unknown")
    vaccine_status: Mapped[str] = mapped_column(String(32), default="unknown")
    deworm_status: Mapped[str] = mapped_column(String(32), default="unknown")
    status: Mapped[str] = mapped_column(String(32), default="active")


class PetGrowthRecord(Base, TimestampMixin):
    __tablename__ = "pet_growth_record"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    pet_id: Mapped[int] = mapped_column(ForeignKey("pet_profile.id"), index=True)
    record_type: Mapped[str] = mapped_column(String(32), index=True)
    title: Mapped[str | None] = mapped_column(String(128))
    content: Mapped[str | None] = mapped_column(Text)
    media_asset_ids: Mapped[str | None] = mapped_column(String(512))
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(32), default="active")


class PetHealthRecord(Base, TimestampMixin):
    __tablename__ = "pet_health_record"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    pet_id: Mapped[int] = mapped_column(ForeignKey("pet_profile.id"), index=True)
    record_type: Mapped[str] = mapped_column(String(32), index=True)
    hospital: Mapped[str | None] = mapped_column(String(128))
    doctor: Mapped[str | None] = mapped_column(String(64))
    description: Mapped[str | None] = mapped_column(Text)
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(32), default="active")


class PetReminder(Base, TimestampMixin):
    __tablename__ = "pet_reminder"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    pet_id: Mapped[int | None] = mapped_column(ForeignKey("pet_profile.id"), index=True)
    reminder_type: Mapped[str] = mapped_column(String(32), index=True)
    title: Mapped[str] = mapped_column(String(128))
    remind_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    status: Mapped[str] = mapped_column(String(32), default="pending")
