from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.response import success
from app.models.user import User
from app.schemas.auth import PasswordLoginIn, PasswordSetIn, SmsLoginIn
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/login/sms")
def login_by_sms(payload: SmsLoginIn, db: Session = Depends(get_db)):
    token = AuthService(db).login_by_sms(payload.phone, payload.code)
    return success(token.model_dump())


@router.post("/login/password")
def login_by_password(payload: PasswordLoginIn, db: Session = Depends(get_db)):
    token = AuthService(db).login_by_password(payload.phone, payload.password)
    return success(token.model_dump())


@router.post("/password")
def set_password(
    payload: PasswordSetIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    AuthService(db).set_password(current_user, payload.password)
    return success({"password_set": True})


@router.post("/logout")
def logout(_: User = Depends(get_current_user)):
    return success({"logged_out": True})
