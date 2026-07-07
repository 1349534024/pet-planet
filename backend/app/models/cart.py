from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.product import Product, ProductSku


class CartItem(Base, TimestampMixin):
    __tablename__ = "cart_item"
    __table_args__ = (UniqueConstraint("user_id", "sku_id", name="uq_cart_item_user_sku"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), index=True)
    sku_id: Mapped[int] = mapped_column(ForeignKey("product_sku.id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    selected: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)

    product: Mapped[Product] = relationship(lazy="selectin")
    sku: Mapped[ProductSku] = relationship(lazy="selectin")
