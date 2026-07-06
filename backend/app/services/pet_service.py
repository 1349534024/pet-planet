from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.errors import AppException, ErrorCode
from app.core.pagination import PageParams
from app.models.pet import PetGrowthRecord, PetProfile, PetReminder
from app.repositories.pet_repo import PetRepository
from app.schemas.pet import PetCreateIn, PetRecordCreateIn, PetUpdateIn, ReminderCreateIn


class PetService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PetRepository(db)

    def list_pets(self, user_id: int, page: PageParams) -> tuple[list[PetProfile], int]:
        return self.repo.list_by_user(user_id, page)

    def create_pet(self, user_id: int, payload: PetCreateIn) -> PetProfile:
        pet = PetProfile(user_id=user_id, **payload.model_dump())
        return self.repo.create(pet)

    def get_user_pet(self, user_id: int, pet_id: int) -> PetProfile:
        pet = self.repo.get_by_id(pet_id)
        if pet is None or pet.deleted_at is not None:
            raise AppException(ErrorCode.pet_not_found, "宠物档案不存在", 404)
        if pet.user_id != user_id:
            raise AppException(ErrorCode.pet_permission_denied, "无权访问该宠物档案", 403)
        return pet

    def update_pet(self, user_id: int, pet_id: int, payload: PetUpdateIn) -> PetProfile:
        pet = self.get_user_pet(user_id, pet_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(pet, field, value)
        return self.repo.save(pet)

    def delete_pet(self, user_id: int, pet_id: int) -> None:
        pet = self.get_user_pet(user_id, pet_id)
        pet.deleted_at = datetime.now(timezone.utc)
        self.repo.save(pet)

    def list_records(self, user_id: int, pet_id: int) -> list[PetGrowthRecord]:
        self.get_user_pet(user_id, pet_id)
        return self.repo.list_records(user_id, pet_id)

    def create_record(self, user_id: int, pet_id: int, payload: PetRecordCreateIn) -> PetGrowthRecord:
        self.get_user_pet(user_id, pet_id)
        record = PetGrowthRecord(user_id=user_id, pet_id=pet_id, **payload.model_dump())
        return self.repo.create_record(record)

    def create_reminder(self, user_id: int, payload: ReminderCreateIn) -> PetReminder:
        if payload.pet_id:
            self.get_user_pet(user_id, payload.pet_id)
        reminder = PetReminder(user_id=user_id, **payload.model_dump())
        return self.repo.create_reminder(reminder)
