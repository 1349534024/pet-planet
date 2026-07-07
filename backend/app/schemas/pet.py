from datetime import date, datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class PetCreateIn(BaseModel):
    name: str = Field(max_length=64)
    type: str = Field(max_length=32)
    breed: str | None = Field(default=None, max_length=64)
    gender: str = Field(default="unknown", max_length=16)
    birthday: date | None = None
    arrival_date: date | None = None
    weight: str | None = Field(default=None, max_length=32)
    avatar: str | None = Field(default=None, max_length=512)
    sterilized: str = Field(default="unknown", max_length=16)
    vaccine_status: str = Field(default="unknown", max_length=32)
    deworm_status: str = Field(default="unknown", max_length=32)


class PetUpdateIn(BaseModel):
    name: str | None = Field(default=None, max_length=64)
    type: str | None = Field(default=None, max_length=32)
    breed: str | None = Field(default=None, max_length=64)
    gender: str | None = Field(default=None, max_length=16)
    birthday: date | None = None
    arrival_date: date | None = None
    weight: str | None = Field(default=None, max_length=32)
    avatar: str | None = Field(default=None, max_length=512)
    sterilized: str | None = Field(default=None, max_length=16)
    vaccine_status: str | None = Field(default=None, max_length=32)
    deworm_status: str | None = Field(default=None, max_length=32)


class PetOut(ORMModel):
    id: int
    user_id: int
    name: str
    type: str
    breed: str | None
    gender: str
    birthday: date | None
    arrival_date: date | None
    weight: str | None
    avatar: str | None
    sterilized: str
    vaccine_status: str
    deworm_status: str
    status: str


class PetRecordCreateIn(BaseModel):
    record_type: str = Field(max_length=32)
    title: str | None = Field(default=None, max_length=128)
    content: str | None = None
    media_asset_ids: str | None = Field(default=None, max_length=512)
    occurred_at: datetime | None = None


class PetRecordUpdateIn(BaseModel):
    record_type: str | None = Field(default=None, max_length=32)
    title: str | None = Field(default=None, max_length=128)
    content: str | None = None
    media_asset_ids: str | None = Field(default=None, max_length=512)
    occurred_at: datetime | None = None
    status: str | None = Field(default=None, max_length=32)


class PetRecordOut(ORMModel):
    id: int
    pet_id: int
    record_type: str
    title: str | None
    content: str | None
    media_asset_ids: str | None
    occurred_at: datetime | None
    status: str


class ReminderCreateIn(BaseModel):
    pet_id: int | None = None
    reminder_type: str = Field(max_length=32)
    title: str = Field(max_length=128)
    remind_at: datetime
