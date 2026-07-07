from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.pagination import PageParams
from app.models.adoption import AdoptionAgreement, AdoptionApplication, AdoptionFollowUp, AdoptionHandover, AdoptionPet


class AdoptionRepository:
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

    def get_pet(self, pet_id: int) -> AdoptionPet | None:
        return self.db.get(AdoptionPet, pet_id)

    def get_public_pet(self, pet_id: int) -> AdoptionPet | None:
        return self.db.scalar(
            select(AdoptionPet).where(
                AdoptionPet.id == pet_id,
                AdoptionPet.deleted_at.is_(None),
                AdoptionPet.status == "active",
                AdoptionPet.audit_status == "approved",
            )
        )

    def get_application(self, application_id: int) -> AdoptionApplication | None:
        return self.db.get(AdoptionApplication, application_id)

    def get_agreement_by_application(self, application_id: int) -> AdoptionAgreement | None:
        return self.db.scalar(
            select(AdoptionAgreement).where(
                AdoptionAgreement.application_id == application_id,
                AdoptionAgreement.deleted_at.is_(None),
            )
        )

    def get_handover_by_application(self, application_id: int) -> AdoptionHandover | None:
        return self.db.scalar(
            select(AdoptionHandover).where(
                AdoptionHandover.application_id == application_id,
                AdoptionHandover.deleted_at.is_(None),
            )
        )

    def list_public(self, page: PageParams) -> tuple[list[AdoptionPet], int]:
        stmt = select(AdoptionPet).where(
            AdoptionPet.deleted_at.is_(None),
            AdoptionPet.status == "active",
            AdoptionPet.audit_status == "approved",
        )
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(self.db.scalars(stmt.order_by(AdoptionPet.id.desc()).offset(page.offset).limit(page.page_size)))
        return items, total

    def list_mine(self, publisher_id: int) -> list[AdoptionPet]:
        return list(
            self.db.scalars(
                select(AdoptionPet)
                .where(AdoptionPet.publisher_id == publisher_id, AdoptionPet.deleted_at.is_(None))
                .order_by(AdoptionPet.id.desc())
            )
        )

    def list_my_applications(self, applicant_id: int) -> list[AdoptionApplication]:
        return list(
            self.db.scalars(
                select(AdoptionApplication)
                .where(AdoptionApplication.applicant_id == applicant_id, AdoptionApplication.deleted_at.is_(None))
                .order_by(AdoptionApplication.id.desc())
            )
        )

    def list_received_applications(self, publisher_id: int) -> list[AdoptionApplication]:
        stmt = (
            select(AdoptionApplication)
            .join(AdoptionPet, AdoptionApplication.adoption_pet_id == AdoptionPet.id)
            .where(
                AdoptionPet.publisher_id == publisher_id,
                AdoptionPet.deleted_at.is_(None),
                AdoptionApplication.deleted_at.is_(None),
            )
            .order_by(AdoptionApplication.id.desc())
        )
        return list(self.db.scalars(stmt))

    def list_follow_ups(self, application_id: int) -> list[AdoptionFollowUp]:
        return list(
            self.db.scalars(
                select(AdoptionFollowUp)
                .where(AdoptionFollowUp.application_id == application_id, AdoptionFollowUp.deleted_at.is_(None))
                .order_by(AdoptionFollowUp.id.desc())
            )
        )

    def get_follow_up_by_type(self, application_id: int, follow_up_type: str) -> AdoptionFollowUp | None:
        return self.db.scalar(
            select(AdoptionFollowUp).where(
                AdoptionFollowUp.application_id == application_id,
                AdoptionFollowUp.follow_up_type == follow_up_type,
                AdoptionFollowUp.deleted_at.is_(None),
            )
        )
