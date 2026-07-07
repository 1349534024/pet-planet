from sqlalchemy import exists, func, select
from sqlalchemy.orm import Session

from app.core.pagination import PageParams
from app.models.live_pet import LivePet, LivePetCertificate, LivePetMedia


class LivePetRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, item):
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get(self, live_pet_id: int) -> LivePet | None:
        return self.db.get(LivePet, live_pet_id)

    def list_public(self, page: PageParams) -> tuple[list[LivePet], int]:
        has_media = exists().where(
            LivePetMedia.live_pet_id == LivePet.id,
            LivePetMedia.deleted_at.is_(None),
            LivePetMedia.status == "active",
        )
        has_health_certificate = exists().where(
            LivePetCertificate.live_pet_id == LivePet.id,
            LivePetCertificate.deleted_at.is_(None),
            LivePetCertificate.status == "active",
            LivePetCertificate.certificate_type == "health_certificate",
        )
        has_quarantine_certificate = exists().where(
            LivePetCertificate.live_pet_id == LivePet.id,
            LivePetCertificate.deleted_at.is_(None),
            LivePetCertificate.status == "active",
            LivePetCertificate.certificate_type == "quarantine_certificate",
        )
        stmt = select(LivePet).where(
            LivePet.deleted_at.is_(None),
            LivePet.status == "active",
            LivePet.audit_status == "approved",
            LivePet.vaccine_status != "unknown",
            LivePet.deworm_status != "unknown",
            LivePet.vaccine_status != "",
            LivePet.deworm_status != "",
            has_media,
            has_health_certificate,
            has_quarantine_certificate,
        )
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(self.db.scalars(stmt.order_by(LivePet.id.desc()).offset(page.offset).limit(page.page_size)))
        return items, total

    def list_mine(self, publisher_id: int) -> list[LivePet]:
        return list(
            self.db.scalars(
                select(LivePet)
                .where(LivePet.publisher_id == publisher_id, LivePet.deleted_at.is_(None))
                .order_by(LivePet.id.desc())
            )
        )

    def list_media(self, live_pet_id: int) -> list[LivePetMedia]:
        return list(
            self.db.scalars(
                select(LivePetMedia)
                .where(LivePetMedia.live_pet_id == live_pet_id, LivePetMedia.deleted_at.is_(None))
                .order_by(LivePetMedia.sort_order.asc(), LivePetMedia.id.asc())
            )
        )

    def list_certificates(self, live_pet_id: int) -> list[LivePetCertificate]:
        return list(
            self.db.scalars(
                select(LivePetCertificate)
                .where(LivePetCertificate.live_pet_id == live_pet_id, LivePetCertificate.deleted_at.is_(None))
                .order_by(LivePetCertificate.id.desc())
            )
        )
