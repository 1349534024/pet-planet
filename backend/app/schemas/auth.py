from pydantic import BaseModel, Field


class SmsLoginIn(BaseModel):
    phone: str = Field(min_length=5, max_length=32)
    code: str = Field(min_length=4, max_length=8)


class PasswordLoginIn(BaseModel):
    phone: str = Field(min_length=5, max_length=32)
    password: str = Field(min_length=6, max_length=64)


class PasswordSetIn(BaseModel):
    password: str = Field(min_length=6, max_length=64)


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: int
    roles: list[str]
