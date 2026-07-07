from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class AdoptionPet(Base, TimestampMixin):
    __tablename__ = "adoption_pet"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    publisher_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    merchant_id: Mapped[int | None] = mapped_column(ForeignKey("merchant.id"), index=True)
    name: Mapped[str] = mapped_column(String(64))
    type: Mapped[str] = mapped_column(String(32), index=True)
    breed: Mapped[str | None] = mapped_column(String(64))
    gender: Mapped[str] = mapped_column(String(16), default="unknown")
    age_desc: Mapped[str | None] = mapped_column(String(64))
    city: Mapped[str | None] = mapped_column(String(64), index=True)
    health_status: Mapped[str | None] = mapped_column(String(255))
    vaccine_status: Mapped[str] = mapped_column(String(32), default="unknown")
    deworm_status: Mapped[str] = mapped_column(String(32), default="unknown")
    sterilized: Mapped[str] = mapped_column(String(16), default="unknown")
    description: Mapped[str | None] = mapped_column(Text)
    adoption_requirements: Mapped[str | None] = mapped_column(Text)
    media_asset_ids: Mapped[str | None] = mapped_column(String(512))
    audit_status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    audit_reason: Mapped[str | None] = mapped_column(String(255))
    audited_by: Mapped[int | None] = mapped_column(ForeignKey("user.id"), index=True)
    audited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(32), default="active")


class AdoptionApplication(Base, TimestampMixin):
    __tablename__ = "adoption_application"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    adoption_pet_id: Mapped[int] = mapped_column(ForeignKey("adoption_pet.id"), index=True)
    applicant_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    real_name: Mapped[str] = mapped_column(String(64))
    phone: Mapped[str] = mapped_column(String(32))
    city: Mapped[str | None] = mapped_column(String(64))
    housing_status: Mapped[str | None] = mapped_column(String(64))
    pet_experience: Mapped[str | None] = mapped_column(Text)
    monthly_budget: Mapped[str | None] = mapped_column(String(64))
    reason: Mapped[str] = mapped_column(Text)
    accept_follow_up: Mapped[str] = mapped_column(String(16), default="yes")
    accept_agreement: Mapped[str] = mapped_column(String(16), default="yes")
    audit_status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    audit_reason: Mapped[str | None] = mapped_column(String(255))
    audited_by: Mapped[int | None] = mapped_column(ForeignKey("user.id"), index=True)
    audited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(32), default="submitted")


class AdoptionAgreement(Base, TimestampMixin):
    __tablename__ = "adoption_agreement"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("adoption_application.id"), index=True)
    file_asset_id: Mapped[int | None] = mapped_column(ForeignKey("file_asset.id"), index=True)
    signed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(32), default="pending")


class AdoptionHandover(Base, TimestampMixin):
    __tablename__ = "adoption_handover"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("adoption_application.id"), index=True)
    handover_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    handover_location: Mapped[str | None] = mapped_column(String(255))
    note: Mapped[str | None] = mapped_column(Text)
    media_asset_ids: Mapped[str | None] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(32), default="completed")


class AdoptionFollowUp(Base, TimestampMixin):
    __tablename__ = "adoption_follow_up"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("adoption_application.id"), index=True)
    follow_up_type: Mapped[str] = mapped_column(String(32), index=True)
    planned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    content: Mapped[str | None] = mapped_column(Text)
    media_asset_ids: Mapped[str | None] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(32), default="pending")
