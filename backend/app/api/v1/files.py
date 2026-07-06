from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.core.response import success
from app.models.user import User
from app.schemas.file import UploadTokenIn
from app.services.file_service import FileService

router = APIRouter()


@router.post("/upload-token")
def create_upload_token(payload: UploadTokenIn, current_user: User = Depends(get_current_user)):
    token = FileService().create_upload_token(current_user.id, payload)
    return success(token.model_dump())
