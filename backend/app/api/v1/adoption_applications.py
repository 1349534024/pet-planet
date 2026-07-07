from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.response import success
from app.models.user import User
from app.schemas.adoption import (
    AdoptionApplicationCreateIn,
    AdoptionApplicationDecisionIn,
    AdoptionApplicationOut,
    AdoptionAgreementCreateIn,
    AdoptionAgreementOut,
    AdoptionFollowUpOut,
    AdoptionHandoverCreateIn,
    AdoptionHandoverOut,
)
from app.services.adoption_service import AdoptionService

router = APIRouter()


@router.post("")
def create_application(
    payload: AdoptionApplicationCreateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    application = AdoptionService(db).apply(current_user.id, payload)
    return success(AdoptionApplicationOut.model_validate(application).model_dump())


@router.get("/me")
def list_my_applications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = AdoptionService(db).list_my_applications(current_user.id)
    return success([AdoptionApplicationOut.model_validate(item).model_dump() for item in items])


@router.get("/received")
def list_received_applications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = AdoptionService(db).list_received_applications(current_user.id)
    return success([AdoptionApplicationOut.model_validate(item).model_dump() for item in items])


@router.post("/{application_id}/approve")
def approve_application(
    application_id: int,
    payload: AdoptionApplicationDecisionIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    application = AdoptionService(db).approve_application(current_user.id, application_id, payload)
    return success(AdoptionApplicationOut.model_validate(application).model_dump())


@router.post("/{application_id}/reject")
def reject_application(
    application_id: int,
    payload: AdoptionApplicationDecisionIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    application = AdoptionService(db).reject_application(current_user.id, application_id, payload)
    return success(AdoptionApplicationOut.model_validate(application).model_dump())


@router.post("/{application_id}/agreement")
def create_or_update_agreement(
    application_id: int,
    payload: AdoptionAgreementCreateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    agreement = AdoptionService(db).create_or_update_agreement(current_user.id, application_id, payload)
    return success(AdoptionAgreementOut.model_validate(agreement).model_dump())


@router.get("/{application_id}/agreement")
def get_agreement(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    agreement = AdoptionService(db).get_agreement(current_user.id, application_id)
    return success(AdoptionAgreementOut.model_validate(agreement).model_dump())


@router.post("/{application_id}/handover")
def create_or_update_handover(
    application_id: int,
    payload: AdoptionHandoverCreateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    handover = AdoptionService(db).create_or_update_handover(current_user.id, application_id, payload)
    return success(AdoptionHandoverOut.model_validate(handover).model_dump())


@router.get("/{application_id}/handover")
def get_handover(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    handover = AdoptionService(db).get_handover(current_user.id, application_id)
    return success(AdoptionHandoverOut.model_validate(handover).model_dump())


@router.post("/{application_id}/follow-up-plan")
def generate_follow_up_plan(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AdoptionService(db)
    service.get_received_application(current_user.id, application_id)
    handover = service.get_handover(current_user.id, application_id)
    follow_ups = service.generate_follow_up_plan(application_id, handover.handover_at)
    return success([AdoptionFollowUpOut.model_validate(item).model_dump() for item in follow_ups])
