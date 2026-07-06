from pydantic import BaseModel, Field


class UploadTokenIn(BaseModel):
    file_name: str = Field(max_length=255)
    file_type: str = Field(max_length=64)
    size_bytes: int | None = None


class UploadTokenOut(BaseModel):
    upload_url: str
    storage_path: str
    public_url: str
    method: str = "PUT"
    headers: dict[str, str] = {}
