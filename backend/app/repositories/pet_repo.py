from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.pagination import PageParams
from app.models.pet import PetGrowthRecord, PetProfile, PetReminder


class PetRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, pet_id: int) -> PetProfile | None:
        return self.db.get(PetProfile, pet_id)

    def get_record_by_id(self, record_id: int) -> PetGrowthRecord | None:
        return self.db.get(PetGrowthRecord, record_id)

    def list_by_user(self, user_id: int, page: PageParams) -> tuple[list[PetProfile], int]:
        stmt = select(PetProfile).where(PetProfile.user_id == user_id, PetProfile.deleted_at.is_(None))
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(self.db.scalars(stmt.order_by(PetProfile.id.desc()).offset(page.offset).limit(page.page_size)))
        return items, total

    def create(self, pet: PetProfile) -> PetProfile:
        self.db.add(pet)
        self.db.commit()
        self.db.refresh(pet)
        return pet

    def save(self, pet: PetProfile) -> PetProfile:
        self.db.add(pet)
        self.db.commit()
        self.db.refresh(pet)
        return pet

    def list_records(self, user_id: int, pet_id: int) -> list[PetGrowthRecord]:
        return list(
            self.db.scalars(
                select(PetGrowthRecord)
                .where(
                    PetGrowthRecord.user_id == user_id,
                    PetGrowthRecord.pet_id == pet_id,
                    PetGrowthRecord.deleted_at.is_(None),
                )
                .order_by(PetGrowthRecord.occurred_at.desc(), PetGrowthRecord.id.desc())
            )
        )

    def create_record(self, record: PetGrowthRecord) -> PetGrowthRecord:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def save_record(self, record: PetGrowthRecord) -> PetGrowthRecord:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def create_reminder(self, reminder: PetReminder) -> PetReminder:
        self.db.add(reminder)
        self.db.commit()
        self.db.refresh(reminder)
        return reminder
