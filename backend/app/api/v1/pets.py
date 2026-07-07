from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.pagination import PageParams, get_page_params
from app.core.response import page_response, success
from app.models.user import User
from app.schemas.pet import (
    PetCreateIn,
    PetOut,
    PetRecordCreateIn,
    PetRecordOut,
    PetRecordUpdateIn,
    PetUpdateIn,
    ReminderCreateIn,
)
from app.services.pet_service import PetService

router = APIRouter()


@router.get("")
def list_pets(
    page: PageParams = Depends(get_page_params),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items, total = PetService(db).list_pets(current_user.id, page)
    return page_response([PetOut.model_validate(item).model_dump() for item in items], page.page, page.page_size, total)


@router.post("")
def create_pet(payload: PetCreateIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pet = PetService(db).create_pet(current_user.id, payload)
    return success(PetOut.model_validate(pet).model_dump())


@router.get("/{pet_id}")
def get_pet(pet_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pet = PetService(db).get_user_pet(current_user.id, pet_id)
    return success(PetOut.model_validate(pet).model_dump())


@router.patch("/{pet_id}")
def update_pet(
    pet_id: int,
    payload: PetUpdateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pet = PetService(db).update_pet(current_user.id, pet_id, payload)
    return success(PetOut.model_validate(pet).model_dump())


@router.delete("/{pet_id}")
def delete_pet(pet_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    PetService(db).delete_pet(current_user.id, pet_id)
    return success({"deleted": True})


@router.get("/{pet_id}/records")
def list_pet_records(pet_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = PetService(db).list_records(current_user.id, pet_id)
    return success([PetRecordOut.model_validate(item).model_dump() for item in records])


@router.post("/{pet_id}/records")
def create_pet_record(
    pet_id: int,
    payload: PetRecordCreateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = PetService(db).create_record(current_user.id, pet_id, payload)
    return success(PetRecordOut.model_validate(record).model_dump())


@router.get("/{pet_id}/records/{record_id}")
def get_pet_record(
    pet_id: int,
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = PetService(db).get_user_record(current_user.id, pet_id, record_id)
    return success(PetRecordOut.model_validate(record).model_dump())


@router.patch("/{pet_id}/records/{record_id}")
def update_pet_record(
    pet_id: int,
    record_id: int,
    payload: PetRecordUpdateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = PetService(db).update_record(current_user.id, pet_id, record_id, payload)
    return success(PetRecordOut.model_validate(record).model_dump())


@router.delete("/{pet_id}/records/{record_id}")
def delete_pet_record(
    pet_id: int,
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    PetService(db).delete_record(current_user.id, pet_id, record_id)
    return success({"deleted": True})


@router.post("/reminders")
def create_reminder(
    payload: ReminderCreateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reminder = PetService(db).create_reminder(current_user.id, payload)
    return success({"id": reminder.id, "status": reminder.status})
