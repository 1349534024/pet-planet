from datetime import date

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class LivePetCreateIn(BaseModel):
    merchant_id: int
    name: str = Field(max_length=64)
    type: str = Field(max_length=32)
    breed: str | None = Field(default=None, max_length=64)
    gender: str = Field(default="unknown", max_length=16)
    birthday: date | None = None
    color: str | None = Field(default=None, max_length=64)
    weight: str | None = Field(default=None, max_length=32)
    city: str | None = Field(default=None, max_length=64)
    price_cent: int = 0
    deposit_cent: int = 0
    vaccine_status: str = Field(default="unknown", max_length=32)
    deworm_status: str = Field(default="unknown", max_length=32)
    health_desc: str | None = None
    description: str | None = None
    support_video_view: str = Field(default="no", max_length=16)
    support_offline_view: str = Field(default="no", max_length=16)


class LivePetOut(ORMModel):
    id: int
    merchant_id: int
    publisher_id: int
    name: str
    type: str
    breed: str | None
    gender: str
    birthday: date | None
    color: str | None
    weight: str | None
    city: str | None
    price_cent: int
    deposit_cent: int
    vaccine_status: str
    deworm_status: str
    health_desc: str | None
    description: str | None
    support_video_view: str
    support_offline_view: str
    audit_status: str
    audit_reason: str | None
    status: str


class LivePetMediaCreateIn(BaseModel):
    file_asset_id: int | None = None
    media_type: str = Field(max_length=32)
    sort_order: int = 0


class LivePetMediaOut(ORMModel):
    id: int
    live_pet_id: int
    file_asset_id: int | None
    media_type: str
    sort_order: int
    status: str


class LivePetCertificateCreateIn(BaseModel):
    certificate_type: str = Field(max_length=64)
    file_asset_id: int | None = None
    certificate_no: str | None = Field(default=None, max_length=128)
    issued_at: date | None = None


class LivePetCertificateOut(ORMModel):
    id: int
    live_pet_id: int
    certificate_type: str
    file_asset_id: int | None
    certificate_no: str | None
    issued_at: date | None
    status: str


class LivePetAuditStatusOut(ORMModel):
    id: int
    audit_status: str
    audit_reason: str | None
    status: str
    has_media: bool
    has_health_certificate: bool
    has_quarantine_certificate: bool
    has_vaccine_info: bool
    has_deworm_info: bool
    ready_for_audit: bool
    can_be_listed: bool
    missing_requirements: list[str]
