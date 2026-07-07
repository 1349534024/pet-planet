from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.order import MallOrder
from app.models.payment import PaymentOrder
from app.models.product import ProductSku


class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_order_for_update(self, user_id: int, order_id: int) -> MallOrder | None:
        stmt = (
            select(MallOrder)
            .options(selectinload(MallOrder.items))
            .where(MallOrder.id == order_id, MallOrder.user_id == user_id, MallOrder.deleted_at.is_(None))
            .with_for_update()
        )
        return self.db.scalar(stmt)

    def get_payment(self, user_id: int, payment_id: int) -> PaymentOrder | None:
        return self.db.scalar(
            select(PaymentOrder).where(
                PaymentOrder.id == payment_id,
                PaymentOrder.user_id == user_id,
                PaymentOrder.deleted_at.is_(None),
            )
        )

    def get_payment_for_update(self, user_id: int, payment_id: int) -> PaymentOrder | None:
        stmt = (
            select(PaymentOrder)
            .where(
                PaymentOrder.id == payment_id,
                PaymentOrder.user_id == user_id,
                PaymentOrder.deleted_at.is_(None),
            )
            .with_for_update()
        )
        return self.db.scalar(stmt)

    def get_by_payment_no_for_update(self, payment_no: str) -> PaymentOrder | None:
        stmt = (
            select(PaymentOrder)
            .where(PaymentOrder.payment_no == payment_no, PaymentOrder.deleted_at.is_(None))
            .with_for_update()
        )
        return self.db.scalar(stmt)

    def get_by_idempotency_key(self, user_id: int, idempotency_key: str) -> PaymentOrder | None:
        return self.db.scalar(
            select(PaymentOrder).where(
                PaymentOrder.user_id == user_id,
                PaymentOrder.idempotency_key == idempotency_key,
                PaymentOrder.deleted_at.is_(None),
            )
        )

    def get_active_by_order_id(self, user_id: int, order_id: int) -> PaymentOrder | None:
        return self.db.scalar(
            select(PaymentOrder)
            .where(
                PaymentOrder.user_id == user_id,
                PaymentOrder.order_id == order_id,
                PaymentOrder.deleted_at.is_(None),
                PaymentOrder.status.in_(["pending", "paid"]),
            )
            .order_by(PaymentOrder.id.desc())
        )

    def get_sku_for_update(self, sku_id: int) -> ProductSku | None:
        return self.db.scalar(select(ProductSku).where(ProductSku.id == sku_id).with_for_update())

    def save(self, payment: PaymentOrder) -> PaymentOrder:
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment
