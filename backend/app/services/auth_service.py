from sqlalchemy.orm import Session

from app.core.errors import AppException, ErrorCode
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.auth import TokenOut


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def login_by_sms(self, phone: str, code: str) -> TokenOut:
        if code != "123456":
            raise AppException(ErrorCode.auth_invalid_code, "验证码错误，开发环境默认验证码为 123456")
        user = UserRepository(self.db).get_or_create_by_phone(phone)
        return self._build_token(user.id, self._active_role_codes(user))

    def login_by_password(self, phone: str, password: str) -> TokenOut:
        repo = UserRepository(self.db)
        user = repo.get_by_phone(phone)
        auth = repo.get_auth("password", phone)
        if user is None or auth is None or auth.credential is None:
            raise AppException(ErrorCode.auth_invalid_password, "手机号或密码错误")
        if not verify_password(password, auth.credential):
            raise AppException(ErrorCode.auth_invalid_password, "密码错误")
        return self._build_token(user.id, self._active_role_codes(user))

    def set_password(self, user: User, password: str) -> None:
        UserRepository(self.db).set_password(user, hash_password(password))

    def _active_role_codes(self, user: User) -> list[str]:
        return [role.code for role in user.roles if role.status == "active"]

    def _build_token(self, user_id: int, roles: list[str]) -> TokenOut:
        subject = str(user_id)
        return TokenOut(
            access_token=create_access_token(subject, {"roles": roles}),
            refresh_token=create_refresh_token(subject),
            user_id=user_id,
            roles=roles,
        )
