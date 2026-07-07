from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.pagination import PageParams
from app.models.merchant import Merchant, MerchantQualification, MerchantStore


class MerchantRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, item):
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get(self, model, item_id: int):
        return self.db.get(model, item_id)

    def list_by_owner(self, owner_id: int) -> list[Merchant]:
        return list(
            self.db.scalars(
                select(Merchant).where(Merchant.owner_id == owner_id, Merchant.deleted_at.is_(None)).order_by(Merchant.id.desc())
            )
        )

    def list_approved(self, page: PageParams) -> tuple[list[Merchant], int]:
        stmt = select(Merchant).where(
            Merchant.deleted_at.is_(None),
            Merchant.status == "active",
            Merchant.audit_status == "approved",
        )
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(self.db.scalars(stmt.order_by(Merchant.id.desc()).offset(page.offset).limit(page.page_size)))
        return items, total

    def list_stores(self, merchant_id: int) -> list[MerchantStore]:
        return list(
            self.db.scalars(
                select(MerchantStore)
                .where(MerchantStore.merchant_id == merchant_id, MerchantStore.deleted_at.is_(None))
                .order_by(MerchantStore.id.desc())
            )
        )

    def list_qualifications(self, merchant_id: int) -> list[MerchantQualification]:
        return list(
            self.db.scalars(
                select(MerchantQualification)
                .where(MerchantQualification.merchant_id == merchant_id, MerchantQualification.deleted_at.is_(None))
                .order_by(MerchantQualification.id.desc())
            )
        )

