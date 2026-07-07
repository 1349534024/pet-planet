from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.cart import CartItem


class CartRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_user_items(self, user_id: int) -> list[CartItem]:
        stmt = (
            select(CartItem)
            .options(selectinload(CartItem.product), selectinload(CartItem.sku))
            .where(CartItem.user_id == user_id, CartItem.deleted_at.is_(None), CartItem.status == "active")
            .order_by(CartItem.updated_at.desc(), CartItem.id.desc())
        )
        return list(self.db.scalars(stmt))

    def get_user_item(self, user_id: int, item_id: int) -> CartItem | None:
        stmt = (
            select(CartItem)
            .options(selectinload(CartItem.product), selectinload(CartItem.sku))
            .where(
                CartItem.id == item_id,
                CartItem.user_id == user_id,
                CartItem.deleted_at.is_(None),
                CartItem.status == "active",
            )
        )
        return self.db.scalar(stmt)

    def get_user_item_by_sku(self, user_id: int, sku_id: int) -> CartItem | None:
        stmt = (
            select(CartItem)
            .options(selectinload(CartItem.product), selectinload(CartItem.sku))
            .where(CartItem.user_id == user_id, CartItem.sku_id == sku_id)
        )
        return self.db.scalar(stmt)

    def save(self, item: CartItem) -> CartItem:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def save_many(self, items: list[CartItem]) -> list[CartItem]:
        for item in items:
            self.db.add(item)
        self.db.commit()
        for item in items:
            self.db.refresh(item)
        return items
