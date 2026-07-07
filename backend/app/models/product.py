from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class ProductCategory(Base, TimestampMixin):
    __tablename__ = "product_category"
    __table_args__ = (UniqueConstraint("code", name="uq_product_category_code"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("product_category.id"), index=True)
    name: Mapped[str] = mapped_column(String(64), index=True)
    code: Mapped[str] = mapped_column(String(64), index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    icon_url: Mapped[str | None] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)


class Brand(Base, TimestampMixin):
    __tablename__ = "brand"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    logo_url: Mapped[str | None] = mapped_column(String(512))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)


class Product(Base, TimestampMixin):
    __tablename__ = "product"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    merchant_id: Mapped[int | None] = mapped_column(Integer, index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("product_category.id"), index=True)
    brand_id: Mapped[int | None] = mapped_column(ForeignKey("brand.id"), index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    subtitle: Mapped[str | None] = mapped_column(String(255))
    main_image: Mapped[str | None] = mapped_column(String(512))
    images: Mapped[str | None] = mapped_column(Text)
    video_url: Mapped[str | None] = mapped_column(String(512))
    description: Mapped[str | None] = mapped_column(Text)
    detail_html: Mapped[str | None] = mapped_column(Text)
    price_cent: Mapped[int] = mapped_column(Integer, index=True)
    original_price_cent: Mapped[int | None] = mapped_column(Integer)
    sales_count: Mapped[int] = mapped_column(Integer, default=0, index=True)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    rating: Mapped[int] = mapped_column(Integer, default=0)
    applicable_pet: Mapped[str | None] = mapped_column(String(128))
    applicable_age: Mapped[str | None] = mapped_column(String(128))
    origin_place: Mapped[str | None] = mapped_column(String(128))
    shelf_life: Mapped[str | None] = mapped_column(String(128))
    ingredients: Mapped[str | None] = mapped_column(Text)
    usage_instructions: Mapped[str | None] = mapped_column(Text)
    notice: Mapped[str | None] = mapped_column(Text)
    shipping_note: Mapped[str | None] = mapped_column(Text)
    after_sale_policy: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="draft", index=True)

    category: Mapped[ProductCategory] = relationship(lazy="selectin")
    brand: Mapped[Brand | None] = relationship(lazy="selectin")
    skus: Mapped[list["ProductSku"]] = relationship(back_populates="product", lazy="selectin")


class ProductSku(Base, TimestampMixin):
    __tablename__ = "product_sku"
    __table_args__ = (UniqueConstraint("sku_code", name="uq_product_sku_code"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), index=True)
    sku_code: Mapped[str] = mapped_column(String(64), index=True)
    sku_name: Mapped[str] = mapped_column(String(128))
    specs: Mapped[str | None] = mapped_column(Text)
    price_cent: Mapped[int] = mapped_column(Integer)
    original_price_cent: Mapped[int | None] = mapped_column(Integer)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    locked_stock: Mapped[int] = mapped_column(Integer, default=0)
    main_image: Mapped[str | None] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)

    product: Mapped[Product] = relationship(back_populates="skus")


class InventoryLog(Base, TimestampMixin):
    __tablename__ = "inventory_log"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), index=True)
    sku_id: Mapped[int] = mapped_column(ForeignKey("product_sku.id"), index=True)
    change_type: Mapped[str] = mapped_column(String(32), index=True)
    change_quantity: Mapped[int] = mapped_column(Integer)
    stock_before: Mapped[int] = mapped_column(Integer)
    stock_after: Mapped[int] = mapped_column(Integer)
    related_type: Mapped[str | None] = mapped_column(String(64), index=True)
    related_id: Mapped[str | None] = mapped_column(String(64), index=True)
    remark: Mapped[str | None] = mapped_column(String(255))
