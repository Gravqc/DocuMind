from __future__ import annotations

import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentStatus


class DocumentsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, document_id: uuid.UUID) -> Document | None:
        return await self._session.get(Document, document_id)

    async def get_by_file_key(self, file_key: str) -> Document | None:
        res = await self._session.execute(select(Document).where(Document.file_key == file_key))
        return res.scalar_one_or_none()

    async def create(self, *, file_key: str, filename: str) -> Document:
        doc = Document(file_key=file_key, filename=filename, status=DocumentStatus.UPLOADED)
        self._session.add(doc)
        await self._session.flush()
        return doc

    async def set_status(
        self,
        *,
        document_id: uuid.UUID,
        status: DocumentStatus,
        error_message: str | None = None,
    ) -> None:
        await self._session.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(status=status, error_message=error_message)
        )

