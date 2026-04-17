from __future__ import annotations

import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import Chunk


class ChunksRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_by_document(self, document_id: uuid.UUID) -> list[Chunk]:
        res = await self._session.execute(
            select(Chunk).where(Chunk.document_id == document_id).order_by(Chunk.chunk_index.asc())
        )
        return list(res.scalars().all())

    async def delete_by_document(self, document_id: uuid.UUID) -> None:
        await self._session.execute(delete(Chunk).where(Chunk.document_id == document_id))

    async def bulk_create(self, chunks: list[Chunk]) -> None:
        self._session.add_all(chunks)
        await self._session.flush()

    async def get_by_ids(self, chunk_ids: list[uuid.UUID]) -> list[Chunk]:
        if not chunk_ids:
            return []
        res = await self._session.execute(select(Chunk).where(Chunk.id.in_(chunk_ids)))
        return list(res.scalars().all())

