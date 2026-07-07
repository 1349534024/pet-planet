from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class CartItemAddIn(BaseModel):
    sku_id: int
    quantity: int = Field(default=1, ge=1, le=999)
    selected: bool = True


class CartItemUpdateIn(BaseModel):
    quantity: int | None = Field(default=None, ge=1, le=999)
    selected: bool | None = None


class CartSelectIn(BaseModel):
    item_ids: list[int] | None = None
    selected: bool = True


class CartItemOut(ORMModel):
    id: int
    user_id: int
    product_id: int
    sku_id: int
    quantity: int
    selected: bool
    status: str
    created_at: datetime
    updated_at: datetime
    product_title: str
    product_main_image: str | None = None
    sku_name: str
    sku_specs: str | None = None
    price_cent: int
    stock: int
    locked_stock: int
    available_stock: int
    line_total_cent: int
    valid: bool
    invalid_reason: str | None = None


class CartOut(BaseModel):
    items: list[CartItemOut]
    total_quantity: int
    selected_quantity: int
    selected_total_cent: int
