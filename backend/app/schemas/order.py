from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class OrderConfirmIn(BaseModel):
    cart_item_ids: list[int] | None = None
    address_id: int
    remark: str | None = Field(default=None, max_length=500)


class OrderCreateIn(OrderConfirmIn):
    pass


class OrderShipIn(BaseModel):
    tracking_company: str | None = Field(default=None, max_length=64)
    tracking_no: str | None = Field(default=None, max_length=128)


class OrderItemConfirmOut(BaseModel):
    cart_item_id: int
    product_id: int
    sku_id: int
    product_title: str
    product_main_image: str | None = None
    sku_name: str
    sku_specs: str | None = None
    unit_price_cent: int
    quantity: int
    total_amount_cent: int
    available_stock: int


class OrderConfirmOut(BaseModel):
    address_id: int
    receiver_name: str
    receiver_phone: str
    province: str
    city: str
    district: str
    detail: str
    items: list[OrderItemConfirmOut]
    total_amount_cent: int
    freight_amount_cent: int
    discount_amount_cent: int
    pay_amount_cent: int


class OrderItemOut(ORMModel):
    id: int
    order_id: int
    order_no: str
    product_id: int
    sku_id: int
    merchant_id: int | None
    product_title: str
    product_main_image: str | None
    sku_name: str
    sku_specs: str | None
    unit_price_cent: int
    quantity: int
    total_amount_cent: int
    status: str


class OrderListOut(ORMModel):
    id: int
    order_no: str
    user_id: int
    total_amount_cent: int
    freight_amount_cent: int
    discount_amount_cent: int
    pay_amount_cent: int
    status: str
    payment_status: str
    tracking_company: str | None = None
    tracking_no: str | None = None
    created_at: datetime
    item_count: int = 0


class OrderDetailOut(ORMModel):
    id: int
    order_no: str
    user_id: int
    address_id: int | None
    receiver_name: str
    receiver_phone: str
    province: str
    city: str
    district: str
    detail: str
    total_amount_cent: int
    freight_amount_cent: int
    discount_amount_cent: int
    pay_amount_cent: int
    status: str
    payment_status: str
    tracking_company: str | None
    tracking_no: str | None
    shipped_at: datetime | None
    received_at: datetime | None
    completed_at: datetime | None
    remark: str | None
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemOut] = Field(default_factory=list)
