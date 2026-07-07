from sqlalchemy.orm import Session
from starlette.status import HTTP_404_NOT_FOUND

from app.core.errors import AppException, ErrorCode
from app.core.permissions import normalize_role_codes
from app.models.user import Role, User
from app.repositories.user_repo import UserRepository


class RoleService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)

    def list_roles(self) -> list[Role]:
        self.repo.ensure_default_roles()
        return self.repo.list_roles()

    def update_user_roles(self, user_id: int, role_codes: list[str]) -> User:
        self.repo.ensure_default_roles()
        normalized_codes = normalize_role_codes(role_codes)
        roles = self.repo.get_roles_by_codes(normalized_codes)
        found_codes = {role.code for role in roles}
        missing_codes = sorted(set(normalized_codes) - found_codes)
        if missing_codes:
            raise AppException(ErrorCode.not_found, f"角色不存在: {', '.join(missing_codes)}", HTTP_404_NOT_FOUND)
        user = self.repo.get_by_id(user_id)
        if user is None:
            raise AppException(ErrorCode.user_not_found, "用户不存在", HTTP_404_NOT_FOUND)
        return self.repo.set_user_roles(user, roles)
