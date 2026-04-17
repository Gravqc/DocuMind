from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PresignedUpload:
    upload_url: str
    file_key: str
    expires_at: int


class StorageService:
    async def create_presigned_upload(self, *, filename: str, content_type: str | None) -> PresignedUpload:
        raise NotImplementedError

    async def put_bytes(self, *, file_key: str, data: bytes) -> None:
        raise NotImplementedError

    async def get_bytes(self, *, file_key: str) -> bytes:
        raise NotImplementedError

