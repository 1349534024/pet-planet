from collections.abc import Generator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from app.core.errors import AppException, ErrorCode
from app.core.security import decode_token
from app.db.session import SessionLocal
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
        role_codes = {role.code for role in current_user.roles}
        if not set(roles).intersection(role_codes):
            raise AppException(ErrorCode.forbidden, "没有操作权限", HTTP_403_FORBIDDEN)
        return current_user

    return checker
