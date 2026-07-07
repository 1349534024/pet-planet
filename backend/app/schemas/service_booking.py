from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class ServiceItemCreateIn(BaseModel):
    merchant_id: int
    store_id: int | None = None
    name: str = Field(max_length=128)
    service_type: str = Field(max_length=32)
    price_cent: int = 0
    duration_minutes: int | None = None
    applicable_pet_type: str | None = Field(default=None, max_length=64)
    description: str | None = None
    refund_rule: str | None = None


class ServiceItemOut(ORMModel):
    id: int
    merchant_id: int
    store_id: int | None
    name: str
    service_type: str
    price_cent: int
    duration_minutes: int | None
    applicable_pet_type: str | None
    description: str | None
    refund_rule: str | None
    audit_status: str
    audit_reason: str | None
    status: str


class ServiceScheduleCreateIn(BaseModel):
    start_at: datetime
    end_at: datetime
    capacity: int = 1


class ServiceScheduleOut(ORMModel):
    id: int
    service_item_id: int
    start_at: datetime
    end_at: datetime
    capacity: int
    booked_count: int
    status: str


class ServiceBookingCreateIn(BaseModel):
    pet_id: int | None = None
    service_item_id: int
    schedule_id: int | None = None
    contact_name: str = Field(max_length=64)
    contact_phone: str = Field(max_length=32)
    remark: str | None = None


class ServiceBookingOut(ORMModel):
    id: int
    user_id: int
    pet_id: int | None
    service_item_id: int
    schedule_id: int | None
    contact_name: str
    contact_phone: str
    remark: str | None
    status: str


class ServiceReportCreateIn(BaseModel):
    content: str | None = None
    before_media_asset_ids: str | None = Field(default=None, max_length=512)
    during_media_asset_ids: str | None = Field(default=None, max_length=512)
    after_media_asset_ids: str | None = Field(default=None, max_length=512)
    abnormal_note: str | None = None


class ServiceReportOut(ORMModel):
    id: int
    booking_id: int
    reporter_id: int
    content: str | None
    before_media_asset_ids: str | None
    during_media_asset_ids: str | None
    after_media_asset_ids: str | None
    abnormal_note: str | None
    status: str
