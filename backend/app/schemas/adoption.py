from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class AdoptionPetCreateIn(BaseModel):
    merchant_id: int | None = None
    name: str = Field(max_length=64)
    type: str = Field(max_length=32)
    breed: str | None = Field(default=None, max_length=64)
    gender: str = Field(default="unknown", max_length=16)
    age_desc: str | None = Field(default=None, max_length=64)
    city: str | None = Field(default=None, max_length=64)
    health_status: str | None = Field(default=None, max_length=255)
    vaccine_status: str = Field(default="unknown", max_length=32)
    deworm_status: str = Field(default="unknown", max_length=32)
    sterilized: str = Field(default="unknown", max_length=16)
    description: str | None = None
    adoption_requirements: str | None = None
    media_asset_ids: str | None = Field(default=None, max_length=512)


class AdoptionPetOut(ORMModel):
    id: int
    publisher_id: int
    merchant_id: int | None
    name: str
    type: str
    breed: str | None
    gender: str
    age_desc: str | None
    city: str | None
    health_status: str | None
    vaccine_status: str
    deworm_status: str
    sterilized: str
    description: str | None
    adoption_requirements: str | None
    media_asset_ids: str | None
    audit_status: str
    audit_reason: str | None
    status: str


class AdoptionApplicationCreateIn(BaseModel):
    adoption_pet_id: int | None = None
    real_name: str = Field(max_length=64)
    phone: str = Field(max_length=32)
    city: str | None = Field(default=None, max_length=64)
    housing_status: str | None = Field(default=None, max_length=64)
    pet_experience: str | None = None
    monthly_budget: str | None = Field(default=None, max_length=64)
    reason: str
    accept_follow_up: str = Field(default="yes", max_length=16)
    accept_agreement: str = Field(default="yes", max_length=16)


class AdoptionApplicationOut(ORMModel):
    id: int
    adoption_pet_id: int
    applicant_id: int
    real_name: str
    phone: str
    city: str | None
    housing_status: str | None
    reason: str
    audit_status: str
    audit_reason: str | None
    status: str


class AdoptionApplicationDecisionIn(BaseModel):
    reason: str | None = Field(default=None, max_length=255)


class AdoptionAgreementCreateIn(BaseModel):
    file_asset_id: int | None = None
    signed_at: datetime | None = None
    status: str = Field(default="signed", max_length=32)


class AdoptionAgreementOut(ORMModel):
    id: int
    application_id: int
    file_asset_id: int | None
    signed_at: datetime | None
    status: str


class AdoptionHandoverCreateIn(BaseModel):
    handover_at: datetime | None = None
    handover_location: str | None = Field(default=None, max_length=255)
    note: str | None = None
    media_asset_ids: str | None = Field(default=None, max_length=512)
    status: str = Field(default="completed", max_length=32)


class AdoptionHandoverOut(ORMModel):
    id: int
    application_id: int
    handover_at: datetime | None
    handover_location: str | None
    note: str | None
    media_asset_ids: str | None
    status: str


class AdoptionFollowUpCreateIn(BaseModel):
    application_id: int
    follow_up_type: str = Field(max_length=32)
    planned_at: datetime | None = None
    completed_at: datetime | None = None
    content: str | None = None
    media_asset_ids: str | None = Field(default=None, max_length=512)


class AdoptionFollowUpOut(ORMModel):
    id: int
    application_id: int
    follow_up_type: str
    planned_at: datetime | None
    completed_at: datetime | None
    content: str | None
    media_asset_ids: str | None
    status: str
