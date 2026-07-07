from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.response import success
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.user import AddressCreateIn, AddressOut, UserMeDetailOut, UserMeUpdateIn
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return success(UserMeDetailOut.model_validate(current_user).model_dump())


@router.patch("/me")
def update_me(
    payload: UserMeUpdateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = UserService(db).update_me(current_user, payload)
    return success(UserMeDetailOut.model_validate(user).model_dump())


@router.get("/me/addresses")
def list_addresses(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = UserRepository(db).list_addresses(current_user.id)
    return success([AddressOut.model_validate(item).model_dump() for item in items])


@router.post("/me/addresses")
def create_address(
    payload: AddressCreateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    address = UserService(db).create_address(current_user.id, payload)
    return success(AddressOut.model_validate(address).model_dump())
