from sqlalchemy.orm import Session

from app.core.errors import AppException, ErrorCode
from app.core.security import create_access_token, create_refresh_token
from app.repositories.user_repo import UserRepository
from app.schemas.auth import TokenOut


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def login_by_sms(self, phone: str, code: str) -> TokenOut:
        if code != "123456":
            raise AppException(ErrorCode.auth_invalid_code, "验证码错误，开发环境默认验证码为 123456")
        user = UserRepository(self.db).get_or_create_by_phone(phone)
        return self._build_token(user.id, [role.code for role in user.roles])

    def login_by_password(self, phone: str, password: str) -> TokenOut:
        if not password:
            raise AppException(ErrorCode.auth_invalid_password, "密码错误")
        user = UserRepository(self.db).get_or_create_by_phone(phone)
        return self._build_token(user.id, [role.code for role in user.roles])

    def _build_token(self, user_id: int, roles: list[str]) -> TokenOut:
        subject = str(user_id)
        return TokenOut(
            access_token=create_access_token(subject, {"roles": roles}),
            refresh_token=create_refresh_token(subject),
            user_id=user_id,
            roles=roles,
        )
