from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class RoleOut(ORMModel):
    id: int
    code: str
    name: str
    status: str
    created_at: datetime


class UserRolesOut(BaseModel):
    user_id: int
    roles: list[RoleOut]


class UserRoleUpdateIn(BaseModel):
    role_codes: list[str] = Field(min_length=1, max_length=8)
