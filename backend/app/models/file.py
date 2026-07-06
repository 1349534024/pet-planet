from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class FileAsset(Base, TimestampMixin):
    __tablename__ = "file_asset"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    uploader_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), index=True)
    file_name: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(64))
    storage_path: Mapped[str] = mapped_column(String(512))
    public_url: Mapped[str | None] = mapped_column(String(512))
    size_bytes: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32), default="uploaded")
