from fastapi import APIRouter

from app.api.v1 import auth, files, pets, reminders, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(pets.router, prefix="/pets", tags=["pets"])
api_router.include_router(reminders.router, prefix="/reminders", tags=["reminders"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
