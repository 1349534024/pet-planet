from collections.abc import Generator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from app.core.errors import AppException, ErrorCode
from app.core.permissions import RoleCode
from app.core.security import decode_token
from app.db.session import SessionLocal
from app.models.admin_audit import AdminPermission, AdminRole, AdminRolePermission, AdminUser, AdminUserRole
from app.models.user import User
from app.repositories.user_repo import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise AppException(ErrorCode.unauthorized, "未登录", HTTP_401_UNAUTHORIZED)
    try:
        payload = decode_token(credentials.credentials)
    except JWTError as exc:
        raise AppException(ErrorCode.unauthorized, "无效 token", HTTP_401_UNAUTHORIZED) from exc
    if payload.get("type") != "access":
        raise AppException(ErrorCode.unauthorized, "无效 token 类型", HTTP_401_UNAUTHORIZED)
    user_id = payload.get("sub")
    if not user_id:
        raise AppException(ErrorCode.unauthorized, "无效 token", HTTP_401_UNAUTHORIZED)
    user = UserRepository(db).get_by_id(int(user_id))
    if user is None:
        raise AppException(ErrorCode.user_not_found, "用户不存在", HTTP_401_UNAUTHORIZED)
    if user.status != "active":
        raise AppException(ErrorCode.user_disabled, "用户已禁用", HTTP_403_FORBIDDEN)
    return user


def require_roles(*roles: str):
    def checker(current_user: User = Depends(get_current_user)) -> User:
        role_codes = get_active_role_codes(current_user)
        if not set(roles).intersection(role_codes):
            raise AppException(ErrorCode.forbidden, "没有操作权限", HTTP_403_FORBIDDEN)
        return current_user

    return checker


def require_permission(permission_code: str):
    def checker(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
        stmt = (
            select(AdminRole.code, AdminPermission.code)
            .select_from(AdminUser)
            .join(AdminUserRole, AdminUserRole.admin_user_id == AdminUser.id)
            .join(AdminRole, AdminRole.id == AdminUserRole.role_id)
            .outerjoin(AdminRolePermission, AdminRolePermission.role_id == AdminRole.id)
            .outerjoin(AdminPermission, AdminPermission.id == AdminRolePermission.permission_id)
            .where(
                AdminUser.user_id == current_user.id,
                AdminUser.status == "active",
                AdminUser.deleted_at.is_(None),
                AdminUserRole.status == "active",
                AdminUserRole.deleted_at.is_(None),
                AdminRole.status == "active",
                AdminRole.deleted_at.is_(None),
            )
        )
        rows = db.execute(stmt).all()
        role_codes = {role_code for role_code, _ in rows if role_code}
        permission_codes = {perm_code for _, perm_code in rows if perm_code}

        if "super_admin" in role_codes or "*" in permission_codes or permission_code in permission_codes:
            return current_user

        raise AppException(ErrorCode.forbidden, "No admin permission", HTTP_403_FORBIDDEN)

    return checker


def require_all_roles(*roles: str):
    def checker(current_user: User = Depends(get_current_user)) -> User:
        role_codes = get_active_role_codes(current_user)
        if not set(roles).issubset(role_codes):
            raise AppException(ErrorCode.forbidden, "没有操作权限", HTTP_403_FORBIDDEN)
        return current_user

    return checker


def get_active_role_codes(user: User) -> set[str]:
    return {role.code for role in user.roles if role.status == "active"}


require_user = require_roles(RoleCode.user.value)
require_merchant = require_roles(RoleCode.merchant.value)
require_operator = require_roles(RoleCode.operator.value)
require_admin = require_roles(RoleCode.admin.value)
require_admin_or_operator = require_roles(RoleCode.admin.value, RoleCode.operator.value)
