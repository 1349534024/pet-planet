from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class CategoryCreateIn(BaseModel):
    name: str = Field(max_length=64)
    code: str = Field(max_length=64)
    parent_id: int | None = None
    sort_order: int = 0
    icon_url: str | None = Field(default=None, max_length=512)
    status: str = Field(default="active", max_length=32)


class CategoryUpdateIn(BaseModel):
    name: str | None = Field(default=None, max_length=64)
    code: str | None = Field(default=None, max_length=64)
    parent_id: int | None = None
    sort_order: int | None = None
    icon_url: str | None = Field(default=None, max_length=512)
    status: str | None = Field(default=None, max_length=32)


class CategoryOut(ORMModel):
    id: int
    parent_id: int | None
    name: str
    code: str
    sort_order: int
    icon_url: str | None
    status: str


class CategoryTreeOut(CategoryOut):
    children: list["CategoryTreeOut"] = Field(default_factory=list)


class BrandCreateIn(BaseModel):
    name: str = Field(max_length=128)
    logo_url: str | None = Field(default=None, max_length=512)
    description: str | None = None
    status: str = Field(default="active", max_length=32)


class BrandUpdateIn(BaseModel):
    name: str | None = Field(default=None, max_length=128)
    logo_url: str | None = Field(default=None, max_length=512)
    description: str | None = None
    status: str | None = Field(default=None, max_length=32)


class BrandOut(ORMModel):
    id: int
    name: str
    logo_url: str | None
    description: str | None
    status: str


class ProductSkuCreateIn(BaseModel):
    sku_code: str = Field(max_length=64)
    sku_name: str = Field(max_length=128)
    specs: str | None = None
    price_cent: int = Field(ge=0)
    original_price_cent: int | None = Field(default=None, ge=0)
    stock: int = Field(default=0, ge=0)
    locked_stock: int = Field(default=0, ge=0)
    main_image: str | None = Field(default=None, max_length=512)
    status: str = Field(default="active", max_length=32)


class ProductSkuUpdateIn(BaseModel):
    sku_code: str | None = Field(default=None, max_length=64)
    sku_name: str | None = Field(default=None, max_length=128)
    specs: str | None = None
    price_cent: int | None = Field(default=None, ge=0)
    original_price_cent: int | None = Field(default=None, ge=0)
    stock: int | None = Field(default=None, ge=0)
    locked_stock: int | None = Field(default=None, ge=0)
    main_image: str | None = Field(default=None, max_length=512)
    status: str | None = Field(default=None, max_length=32)


class ProductSkuOut(ORMModel):
    id: int
    product_id: int
    sku_code: str
    sku_name: str
    specs: str | None
    price_cent: int
    original_price_cent: int | None
    stock: int
    locked_stock: int
    main_image: str | None
    status: str


class ProductCreateIn(BaseModel):
    merchant_id: int | None = None
    category_id: int
    brand_id: int | None = None
    title: str = Field(max_length=255)
    subtitle: str | None = Field(default=None, max_length=255)
    main_image: str | None = Field(default=None, max_length=512)
    images: str | None = None
    video_url: str | None = Field(default=None, max_length=512)
    description: str | None = None
    detail_html: str | None = None
    price_cent: int = Field(ge=0)
    original_price_cent: int | None = Field(default=None, ge=0)
    applicable_pet: str | None = Field(default=None, max_length=128)
    applicable_age: str | None = Field(default=None, max_length=128)
    origin_place: str | None = Field(default=None, max_length=128)
    shelf_life: str | None = Field(default=None, max_length=128)
    ingredients: str | None = None
    usage_instructions: str | None = None
    notice: str | None = None
    shipping_note: str | None = None
    after_sale_policy: str | None = None
    status: str = Field(default="on_sale", max_length=32)
    skus: list[ProductSkuCreateIn] = Field(default_factory=list)


class ProductUpdateIn(BaseModel):
    merchant_id: int | None = None
    category_id: int | None = None
    brand_id: int | None = None
    title: str | None = Field(default=None, max_length=255)
    subtitle: str | None = Field(default=None, max_length=255)
    main_image: str | None = Field(default=None, max_length=512)
    images: str | None = None
    video_url: str | None = Field(default=None, max_length=512)
    description: str | None = None
    detail_html: str | None = None
    price_cent: int | None = Field(default=None, ge=0)
    original_price_cent: int | None = Field(default=None, ge=0)
    applicable_pet: str | None = Field(default=None, max_length=128)
    applicable_age: str | None = Field(default=None, max_length=128)
    origin_place: str | None = Field(default=None, max_length=128)
    shelf_life: str | None = Field(default=None, max_length=128)
    ingredients: str | None = None
    usage_instructions: str | None = None
    notice: str | None = None
    shipping_note: str | None = None
    after_sale_policy: str | None = None
    status: str | None = Field(default=None, max_length=32)


class ProductListOut(ORMModel):
    id: int
    merchant_id: int | None
    category_id: int
    brand_id: int | None
    title: str
    subtitle: str | None
    main_image: str | None
    price_cent: int
    original_price_cent: int | None
    sales_count: int
    review_count: int
    rating: int
    status: str
    brand_name: str | None = None
    category_name: str | None = None
    total_stock: int = 0
    available_stock: int = 0
    has_stock: bool = False


class ProductDetailOut(ORMModel):
    id: int
    merchant_id: int | None
    category_id: int
    brand_id: int | None
    title: str
    subtitle: str | None
    main_image: str | None
    images: str | None
    video_url: str | None
    description: str | None
    detail_html: str | None
    price_cent: int
    original_price_cent: int | None
    sales_count: int
    review_count: int
    rating: int
    applicable_pet: str | None
    applicable_age: str | None
    origin_place: str | None
    shelf_life: str | None
    ingredients: str | None
    usage_instructions: str | None
    notice: str | None
    shipping_note: str | None
    after_sale_policy: str | None
    status: str
    created_at: datetime
    category: CategoryOut | None = None
    brand: BrandOut | None = None
    skus: list[ProductSkuOut] = Field(default_factory=list)
