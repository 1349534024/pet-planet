from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.permissions import DEFAULT_ROLE_DEFINITIONS, RoleCode, normalize_role_codes
from app.models.user import Role, User, UserAddress, UserAuth, UserProfile


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_phone(self, phone: str) -> User | None:
        return self.db.scalar(select(User).where(User.phone == phone, User.deleted_at.is_(None)))

    def list_roles(self) -> list[Role]:
        return list(self.db.scalars(select(Role).order_by(Role.id.asc())))

    def get_roles_by_codes(self, role_codes: list[str]) -> list[Role]:
        normalized_codes = normalize_role_codes(role_codes)
        if not normalized_codes:
            return []
        return list(self.db.scalars(select(Role).where(Role.code.in_(normalized_codes))))

    def get_auth(self, auth_type: str, identifier: str) -> UserAuth | None:
        return self.db.scalar(
            select(UserAuth).where(UserAuth.auth_type == auth_type, UserAuth.identifier == identifier)
        )

    def get_or_create_role(self, code: str, name: str) -> Role:
        role = self.db.scalar(select(Role).where(Role.code == code))
        if role:
            return role
        role = Role(code=code, name=name)
        self.db.add(role)
        self.db.flush()
        return role

    def ensure_default_roles(self) -> list[Role]:
        roles = []
        for code, name in DEFAULT_ROLE_DEFINITIONS.items():
            roles.append(self.get_or_create_role(code, name))
        self.db.commit()
        return roles

    def get_or_create_by_phone(self, phone: str) -> User:
        self.ensure_default_roles()
        user = self.get_by_phone(phone)
        if user:
            self.ensure_default_user_role(user)
            return user
        user = User(phone=phone, nickname=f"用户{phone[-4:]}")
        self.db.add(user)
        self.db.flush()
        self.db.add(UserProfile(user_id=user.id))
        self.db.add(UserAuth(user_id=user.id, auth_type="phone", identifier=phone))
        user.roles.append(self.get_or_create_role(RoleCode.user.value, DEFAULT_ROLE_DEFINITIONS[RoleCode.user.value]))
        self.db.commit()
        self.db.refresh(user)
        return user

    def ensure_default_user_role(self, user: User) -> None:
        if any(role.code == RoleCode.user.value for role in user.roles):
            return
        user.roles.append(self.get_or_create_role(RoleCode.user.value, DEFAULT_ROLE_DEFINITIONS[RoleCode.user.value]))
        self.db.commit()
        self.db.refresh(user)

    def set_user_roles(self, user: User, roles: list[Role]) -> User:
        user.roles = roles
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def set_password(self, user: User, password_hash: str) -> None:
        if user.phone is None:
            return
        auth = self.get_auth("password", user.phone)
        if auth is None:
            auth = UserAuth(user_id=user.id, auth_type="password", identifier=user.phone)
            self.db.add(auth)
        auth.credential = password_hash
        self.db.commit()

    def list_addresses(self, user_id: int) -> list[UserAddress]:
        return list(
            self.db.scalars(
                select(UserAddress)
                .where(UserAddress.user_id == user_id, UserAddress.deleted_at.is_(None))
                .order_by(UserAddress.is_default.desc(), UserAddress.id.desc())
            )
        )

    def create_address(self, address: UserAddress) -> UserAddress:
        if address.is_default:
            self.db.query(UserAddress).filter(UserAddress.user_id == address.user_id).update({"is_default": False})
        self.db.add(address)
        self.db.commit()
        self.db.refresh(address)
        return address
