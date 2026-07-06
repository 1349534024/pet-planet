from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class UserMeOut(ORMModel):
    id: int
    phone: str | None
    nickname: str | None
    avatar: str | None
    status: str
    real_name_status: str
    is_guest: bool
    created_at: datetime


class UserMeUpdateIn(BaseModel):
    nickname: str | None = Field(default=None, max_length=64)
    avatar: str | None = Field(default=None, max_length=512)
    city: str | None = Field(default=None, max_length=64)
    signature: str | None = Field(default=None, max_length=255)
    has_pet: bool | None = None
    interest_tags: str | None = Field(default=None, max_length=512)


class AddressCreateIn(BaseModel):
    receiver_name: str = Field(max_length=64)
    receiver_phone: str = Field(max_length=32)
    province: str = Field(max_length=64)
    city: str = Field(max_length=64)
    district: str = Field(max_length=64)
    detail: str = Field(max_length=255)
    is_default: bool = False


class AddressOut(ORMModel):
    id: int
    receiver_name: str
    receiver_phone: str
    province: str
    city: str
    district: str
    detail: str
    is_default: bool
    status: str
