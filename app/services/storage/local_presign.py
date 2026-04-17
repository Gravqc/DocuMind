from __future__ import annotations

import os
import uuid

from app.core.config import settings
from app.services.storage.base import PresignedUpload, StorageService
from app.utils.signing import now_epoch, sign


class LocalPresignedStorage(StorageService):
    def __init__(self, *, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    async def create_presigned_upload(self, *, filename: str, content_type: str | None) -> PresignedUpload:
        file_key = f"{uuid.uuid4()}-{os.path.basename(filename)}"
        expires_at = now_epoch() + 15 * 60

        message = f"{file_key}:{expires_at}"
        sig = sign(secret=settings.presign_secret, message=message)

        upload_url = f"{self._base_url}/storage/upload/{file_key}?expires={expires_at}&sig={sig}"
        return PresignedUpload(upload_url=upload_url, file_key=file_key, expires_at=expires_at)

    async def put_bytes(self, *, file_key: str, data: bytes) -> None:
        uploads_dir = os.path.join(settings.data_dir, "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        path = os.path.join(uploads_dir, file_key)
        with open(path, "wb") as f:
            f.write(data)

    async def get_bytes(self, *, file_key: str) -> bytes:
        path = os.path.join(settings.data_dir, "uploads", file_key)
        with open(path, "rb") as f:
            return f.read()

