from sqlalchemy.orm import Session

from app.models.user import User, UserAddress, UserProfile
from app.repositories.user_repo import UserRepository
from app.schemas.user import AddressCreateIn, UserMeUpdateIn


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)

    def update_me(self, user: User, payload: UserMeUpdateIn) -> User:
        data = payload.model_dump(exclude_unset=True)
        for field in ["nickname", "avatar"]:
            if field in data:
                setattr(user, field, data[field])
        if user.profile is None:
            user.profile = UserProfile(user_id=user.id)
        for field in ["city", "signature", "has_pet", "interest_tags"]:
            if field in data:
                setattr(user.profile, field, data[field])
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def create_address(self, user_id: int, payload: AddressCreateIn) -> UserAddress:
        address = UserAddress(user_id=user_id, **payload.model_dump())
        return self.repo.create_address(address)
