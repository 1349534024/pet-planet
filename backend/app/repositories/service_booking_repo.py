from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.pagination import PageParams
from app.models.service_booking import ServiceBooking, ServiceItem, ServiceReport, ServiceSchedule


class ServiceBookingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, item):
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def save(self, item):
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get(self, model, item_id: int):
        return self.db.get(model, item_id)

    def list_public_items(self, page: PageParams) -> tuple[list[ServiceItem], int]:
        stmt = select(ServiceItem).where(
            ServiceItem.deleted_at.is_(None),
            ServiceItem.status == "active",
            ServiceItem.audit_status == "approved",
        )
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(self.db.scalars(stmt.order_by(ServiceItem.id.desc()).offset(page.offset).limit(page.page_size)))
        return items, total

    def list_merchant_items(self, merchant_id: int) -> list[ServiceItem]:
        return list(
            self.db.scalars(
                select(ServiceItem)
                .where(ServiceItem.merchant_id == merchant_id, ServiceItem.deleted_at.is_(None))
                .order_by(ServiceItem.id.desc())
            )
        )

    def list_my_bookings(self, user_id: int) -> list[ServiceBooking]:
        return list(
            self.db.scalars(
                select(ServiceBooking)
                .where(ServiceBooking.user_id == user_id, ServiceBooking.deleted_at.is_(None))
                .order_by(ServiceBooking.id.desc())
            )
        )

    def list_schedules(self, service_item_id: int) -> list[ServiceSchedule]:
        return list(
            self.db.scalars(
                select(ServiceSchedule)
                .where(ServiceSchedule.service_item_id == service_item_id, ServiceSchedule.deleted_at.is_(None))
                .order_by(ServiceSchedule.start_at.asc())
            )
        )

    def list_reports(self, booking_id: int) -> list[ServiceReport]:
        return list(
            self.db.scalars(
                select(ServiceReport)
                .where(ServiceReport.booking_id == booking_id, ServiceReport.deleted_at.is_(None))
                .order_by(ServiceReport.id.desc())
            )
        )

