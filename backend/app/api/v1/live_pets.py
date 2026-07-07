from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.pagination import PageParams, get_page_params
from app.core.response import page_response, success
from app.models.user import User
from app.schemas.live_pet import (
    LivePetAuditStatusOut,
    LivePetCertificateCreateIn,
    LivePetCertificateOut,
    LivePetCreateIn,
    LivePetMediaCreateIn,
    LivePetMediaOut,
    LivePetOut,
)
from app.services.live_pet_service import LivePetService

router = APIRouter()


@router.get("")
def list_live_pets(page: PageParams = Depends(get_page_params), db: Session = Depends(get_db)):
    items, total = LivePetService(db).list_public(page)
    return page_response([LivePetOut.model_validate(item).model_dump() for item in items], page.page, page.page_size, total)


@router.post("")
def create_live_pet(
    payload: LivePetCreateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    live_pet = LivePetService(db).create(current_user.id, payload)
    return success(LivePetOut.model_validate(live_pet).model_dump())


@router.get("/me")
def list_my_live_pets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = LivePetService(db).list_mine(current_user.id)
    return success([LivePetOut.model_validate(item).model_dump() for item in items])


@router.get("/{live_pet_id}")
def get_live_pet(live_pet_id: int, db: Session = Depends(get_db)):
    live_pet = LivePetService(db).get_public(live_pet_id)
    return success(LivePetOut.model_validate(live_pet).model_dump())


@router.get("/{live_pet_id}/audit-status")
def get_audit_status(
    live_pet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    status = LivePetService(db).get_audit_status(current_user.id, live_pet_id)
    return success(LivePetAuditStatusOut.model_validate(status).model_dump())


@router.post("/{live_pet_id}/media")
def add_media(
    live_pet_id: int,
    payload: LivePetMediaCreateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    media = LivePetService(db).add_media(current_user.id, live_pet_id, payload)
    return success(LivePetMediaOut.model_validate(media).model_dump())


@router.get("/{live_pet_id}/media")
def list_media(live_pet_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = LivePetService(db).list_media(current_user.id, live_pet_id)
    return success([LivePetMediaOut.model_validate(item).model_dump() for item in items])


@router.post("/{live_pet_id}/certificates")
def add_certificate(
    live_pet_id: int,
    payload: LivePetCertificateCreateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    certificate = LivePetService(db).add_certificate(current_user.id, live_pet_id, payload)
    return success(LivePetCertificateOut.model_validate(certificate).model_dump())


@router.get("/{live_pet_id}/certificates")
def list_certificates(live_pet_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = LivePetService(db).list_certificates(current_user.id, live_pet_id)
    return success([LivePetCertificateOut.model_validate(item).model_dump() for item in items])
