from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.pagination import PageParams, get_page_params
from app.core.response import page_response, success
from app.models.user import User
from app.schemas.adoption import (
    AdoptionApplicationCreateIn,
    AdoptionApplicationOut,
    AdoptionFollowUpCreateIn,
    AdoptionFollowUpOut,
    AdoptionPetCreateIn,
    AdoptionPetOut,
)
from app.services.adoption_service import AdoptionService

router = APIRouter()


@router.get("")
def list_adoptions(page: PageParams = Depends(get_page_params), db: Session = Depends(get_db)):
    items, total = AdoptionService(db).list_public(page)
    return page_response([AdoptionPetOut.model_validate(item).model_dump() for item in items], page.page, page.page_size, total)


@router.post("")
def create_adoption(
    payload: AdoptionPetCreateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pet = AdoptionService(db).create_pet(current_user.id, payload)
    return success(AdoptionPetOut.model_validate(pet).model_dump())


@router.get("/me")
def list_my_adoptions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = AdoptionService(db).list_mine(current_user.id)
    return success([AdoptionPetOut.model_validate(item).model_dump() for item in items])


@router.get("/applications/me")
def list_my_applications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = AdoptionService(db).list_my_applications(current_user.id)
    return success([AdoptionApplicationOut.model_validate(item).model_dump() for item in items])


@router.post("/follow-ups")
def create_follow_up(
    payload: AdoptionFollowUpCreateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    follow_up = AdoptionService(db).create_follow_up(current_user.id, payload)
    return success(AdoptionFollowUpOut.model_validate(follow_up).model_dump())


@router.get("/applications/{application_id}/follow-ups")
def list_follow_ups(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = AdoptionService(db).list_follow_ups(current_user.id, application_id)
    return success([AdoptionFollowUpOut.model_validate(item).model_dump() for item in items])


@router.get("/me/{adoption_pet_id}")
def get_my_adoption(
    adoption_pet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pet = AdoptionService(db).get_owned_pet(current_user.id, adoption_pet_id)
    return success(AdoptionPetOut.model_validate(pet).model_dump())


@router.get("/{adoption_pet_id}")
def get_adoption(adoption_pet_id: int, db: Session = Depends(get_db)):
    pet = AdoptionService(db).get_public_pet(adoption_pet_id)
    return success(AdoptionPetOut.model_validate(pet).model_dump())


@router.post("/{adoption_pet_id}/applications")
def create_application(
    adoption_pet_id: int,
    payload: AdoptionApplicationCreateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    payload.adoption_pet_id = adoption_pet_id
    application = AdoptionService(db).apply(current_user.id, payload)
    return success(AdoptionApplicationOut.model_validate(application).model_dump())
