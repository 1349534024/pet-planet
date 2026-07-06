from uuid import uuid4

from app.core.config import settings
from app.schemas.file import UploadTokenIn, UploadTokenOut


class FileService:
    def create_upload_token(self, user_id: int, payload: UploadTokenIn) -> UploadTokenOut:
        suffix = payload.file_name.rsplit(".", 1)[-1] if "." in payload.file_name else "bin"
        storage_path = f"uploads/{user_id}/{uuid4()}.{suffix}"
        public_url = f"{settings.object_storage_public_base_url}/{storage_path}"
        return UploadTokenOut(
            upload_url=public_url,
            storage_path=storage_path,
            public_url=public_url,
            headers={"x-demo-upload": "local-mock"},
        )
