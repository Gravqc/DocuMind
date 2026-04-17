from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import DocumentStatus
from app.repositories.documents import DocumentsRepository
from app.workers.tasks import process_document


class DocumentsService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._docs = DocumentsRepository(session)

    async def confirm_upload(self, *, file_key: str, filename: str) -> uuid.UUID:
        existing = await self._docs.get_by_file_key(file_key)
        if existing:
            doc = existing
        else:
            doc = await self._docs.create(file_key=file_key, filename=filename)

        # If it's a brand new upload (or re-confirm), keep it UPLOADED and enqueue processing.
        await self._docs.set_status(document_id=doc.id, status=DocumentStatus.UPLOADED, error_message=None)
        await self._session.commit()

        process_document.delay(str(doc.id))
        return doc.id

    async def get_status(self, *, document_id: uuid.UUID) -> tuple[DocumentStatus, str | None]:
        doc = await self._docs.get(document_id)
        if not doc:
            raise KeyError("Document not found")
        return doc.status, doc.error_message

