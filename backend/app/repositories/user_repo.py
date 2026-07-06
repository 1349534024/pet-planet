from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import Role, User, UserAddress, UserAuth, UserProfile


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_phone(self, phone: str) -> User | None:
        return self.db.scalar(select(User).where(User.phone == phone, User.deleted_at.is_(None)))

    def get_or_create_by_phone(self, phone: str) -> User:
        user = self.get_by_phone(phone)
        if user:
            return user
        user = User(phone=phone, nickname=f"用户{phone[-4:]}")
        self.db.add(user)
        self.db.flush()
        self.db.add(UserProfile(user_id=user.id))
        self.db.add(UserAuth(user_id=user.id, auth_type="phone", identifier=phone))
        role = self.db.scalar(select(Role).where(Role.code == "user"))
        if role:
            user.roles.append(role)
        self.db.commit()
        self.db.refresh(user)
        return user

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
