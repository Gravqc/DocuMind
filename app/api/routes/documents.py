from __future__ import annotations

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_storage
from app.db.session import get_db
from app.schemas.documents import (
    ConfirmUploadRequest,
    ConfirmUploadResponse,
    DocumentStatusResponse,
    UploadUrlRequest,
    UploadUrlResponse,
)
from app.services.documents import DocumentsService
from app.services.storage.base import StorageService

router = APIRouter(prefix="/documents")


@router.post("/upload-url", response_model=UploadUrlResponse)
async def create_upload_url(
    payload: UploadUrlRequest,
    storage: StorageService = Depends(get_storage),
) -> UploadUrlResponse:
    presigned = await storage.create_presigned_upload(
        filename=payload.filename,
        content_type=payload.content_type,
    )
    return UploadUrlResponse(upload_url=presigned.upload_url, file_key=presigned.file_key)


@router.post("/confirm", response_model=ConfirmUploadResponse)
async def confirm_upload(payload: ConfirmUploadRequest, session: AsyncSession = Depends(get_db)) -> ConfirmUploadResponse:
    service = DocumentsService(session)
    document_id = await service.confirm_upload(file_key=payload.file_key, filename=payload.filename)
    return ConfirmUploadResponse(document_id=str(document_id), status="UPLOADED")


@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
async def document_status(document_id: str, session: AsyncSession = Depends(get_db)) -> DocumentStatusResponse:
    service = DocumentsService(session)
    try:
        doc_id = uuid.UUID(document_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail="Invalid document_id") from e
    try:
        status, error = await service.get_status(document_id=doc_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail="Document not found") from e
    return DocumentStatusResponse(document_id=document_id, status=status.value, error_message=error)

