from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.response import success
from app.models.user import User
from app.schemas.pet import ReminderCreateIn
from app.services.pet_service import PetService

router = APIRouter()


@router.post("")
def create_reminder(
    payload: ReminderCreateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reminder = PetService(db).create_reminder(current_user.id, payload)
    return success({"id": reminder.id, "status": reminder.status})
