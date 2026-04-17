from __future__ import annotations

from pydantic import BaseModel, Field


class UploadUrlRequest(BaseModel):
    filename: str = Field(..., min_length=1, max_length=512)
    content_type: str | None = Field(default=None, max_length=256)


class UploadUrlResponse(BaseModel):
    upload_url: str
    file_key: str


class ConfirmUploadRequest(BaseModel):
    file_key: str = Field(..., min_length=1, max_length=1024)
    filename: str = Field(..., min_length=1, max_length=512)


class ConfirmUploadResponse(BaseModel):
    document_id: str
    status: str


class DocumentStatusResponse(BaseModel):
    document_id: str
    status: str
    error_message: str | None = None

