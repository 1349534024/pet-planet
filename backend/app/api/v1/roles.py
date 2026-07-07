from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_admin
from app.core.response import success
from app.models.user import User
from app.schemas.role import RoleOut, UserRoleUpdateIn, UserRolesOut
from app.services.role_service import RoleService

router = APIRouter()


@router.get("/me")
def get_my_roles(current_user: User = Depends(get_current_user)):
    roles = [RoleOut.model_validate(role).model_dump() for role in current_user.roles if role.status == "active"]
    return success(UserRolesOut(user_id=current_user.id, roles=roles).model_dump())


@router.get("")
def list_roles(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    roles = RoleService(db).list_roles()
    return success([RoleOut.model_validate(role).model_dump() for role in roles])


@router.patch("/users/{user_id}")
def update_user_roles(
    user_id: int,
    payload: UserRoleUpdateIn,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = RoleService(db).update_user_roles(user_id, payload.role_codes)
    return success(
        UserRolesOut(
            user_id=user.id,
            roles=[RoleOut.model_validate(role) for role in user.roles if role.status == "active"],
        ).model_dump()
    )
