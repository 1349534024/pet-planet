from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.pagination import PageParams
from app.models.order import MallOrder
from app.models.product import ProductSku
from app.models.user import UserAddress


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_address(self, user_id: int, address_id: int) -> UserAddress | None:
        return self.db.scalar(
            select(UserAddress).where(
                UserAddress.id == address_id,
                UserAddress.user_id == user_id,
                UserAddress.deleted_at.is_(None),
                UserAddress.status == "active",
            )
        )

    def get_sku_for_update(self, sku_id: int) -> ProductSku | None:
        stmt = select(ProductSku).where(ProductSku.id == sku_id).with_for_update()
        return self.db.scalar(stmt)

    def get_by_id(self, user_id: int, order_id: int) -> MallOrder | None:
        stmt = (
            select(MallOrder)
            .options(selectinload(MallOrder.items))
            .where(MallOrder.id == order_id, MallOrder.user_id == user_id, MallOrder.deleted_at.is_(None))
        )
        return self.db.scalar(stmt)

    def get_by_idempotency_key(self, user_id: int, idempotency_key: str) -> MallOrder | None:
        stmt = (
            select(MallOrder)
            .options(selectinload(MallOrder.items))
            .where(
                MallOrder.user_id == user_id,
                MallOrder.idempotency_key == idempotency_key,
                MallOrder.deleted_at.is_(None),
            )
        )
        return self.db.scalar(stmt)

    def list_user_orders(
        self,
        user_id: int,
        page: PageParams,
        status: str | None = None,
    ) -> tuple[list[MallOrder], int]:
        stmt = (
            select(MallOrder)
            .options(selectinload(MallOrder.items))
            .where(MallOrder.user_id == user_id, MallOrder.deleted_at.is_(None))
        )
        if status:
            stmt = stmt.where(MallOrder.status == status)
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(self.db.scalars(stmt.order_by(MallOrder.id.desc()).offset(page.offset).limit(page.page_size)))
        return items, total

    def save_order(self, order: MallOrder) -> MallOrder:
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order
