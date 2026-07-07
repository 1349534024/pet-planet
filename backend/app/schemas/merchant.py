from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class MerchantCreateIn(BaseModel):
    merchant_type: str = Field(max_length=32)
    name: str = Field(max_length=128)
    contact_name: str = Field(max_length=64)
    contact_phone: str = Field(max_length=32)
    city: str | None = Field(default=None, max_length=64)
    address: str | None = Field(default=None, max_length=255)
    business_scope: str | None = Field(default=None, max_length=255)
    settlement_account: str | None = Field(default=None, max_length=255)


class MerchantOut(ORMModel):
    id: int
    owner_id: int
    merchant_type: str
    name: str
    contact_name: str
    contact_phone: str
    city: str | None
    address: str | None
    business_scope: str | None
    deposit_status: str
    audit_status: str
    audit_reason: str | None
    status: str


class MerchantApplicationStatusOut(MerchantOut):
    required_qualification_types: list[str]
    missing_qualification_types: list[str]
    can_publish_live_pet: bool
    can_publish_service: bool


class MerchantAuditDecisionIn(BaseModel):
    reason: str | None = Field(default=None, max_length=255)


class QualificationCreateIn(BaseModel):
    qualification_type: str = Field(max_length=64)
    file_asset_id: int | None = None
    certificate_no: str | None = Field(default=None, max_length=128)
    description: str | None = None


class QualificationOut(ORMModel):
    id: int
    merchant_id: int
    qualification_type: str
    file_asset_id: int | None
    certificate_no: str | None
    description: str | None
    audit_status: str
    audit_reason: str | None
    status: str


class QualificationAuditDecisionIn(BaseModel):
    reason: str | None = Field(default=None, max_length=255)


class StoreCreateIn(BaseModel):
    name: str = Field(max_length=128)
    province: str | None = Field(default=None, max_length=64)
    city: str | None = Field(default=None, max_length=64)
    district: str | None = Field(default=None, max_length=64)
    address: str = Field(max_length=255)
    contact_phone: str | None = Field(default=None, max_length=32)
    cover_file_asset_id: int | None = None
    longitude: str | None = Field(default=None, max_length=32)
    latitude: str | None = Field(default=None, max_length=32)


class MerchantApplicationCreateIn(MerchantCreateIn):
    qualifications: list[QualificationCreateIn] = Field(default_factory=list)
    stores: list[StoreCreateIn] = Field(default_factory=list)


class StoreOut(ORMModel):
    id: int
    merchant_id: int
    name: str
    province: str | None
    city: str | None
    district: str | None
    address: str
    contact_phone: str | None
    cover_file_asset_id: int | None
    longitude: str | None
    latitude: str | None
    status: str


class MerchantBackendDependencyOut(BaseModel):
    module: str
    owner: str = "B"
    dependency: str
    status: str = "waiting"
    note: str


class MerchantBackendPlaceholderOut(BaseModel):
    merchant_id: int
    capability: str
    ready: bool = False
    dependencies: list[MerchantBackendDependencyOut]
    items: list[dict] = Field(default_factory=list)


class MerchantBusinessSummaryOut(BaseModel):
    merchant_id: int
    ready: bool = False
    order_count: int = 0
    gmv_cent: int = 0
    after_sale_rate: float | None = None
    rating: float | None = None
    dependencies: list[MerchantBackendDependencyOut]
