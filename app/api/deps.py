from __future__ import annotations

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.chunks import ChunksRepository
from app.repositories.faiss import FaissRepository
from app.services.embeddings import OpenAIEmbeddingsService
from app.services.llm import OpenAIChatService
from app.services.storage.base import StorageService
from app.services.storage.local_presign import LocalPresignedStorage
from app.services.chat import ChatService


def get_storage(request: Request) -> StorageService:
    base_url = str(request.base_url).rstrip("/")
    return LocalPresignedStorage(base_url=base_url)


def get_faiss_repo() -> FaissRepository:
    return FaissRepository()


def get_embeddings_service() -> OpenAIEmbeddingsService:
    return OpenAIEmbeddingsService()


def get_llm_service() -> OpenAIChatService:
    return OpenAIChatService()


def get_chunks_repo(session: AsyncSession = Depends(get_db)) -> ChunksRepository:
    return ChunksRepository(session)


def get_chat_service(
    embeddings: OpenAIEmbeddingsService = Depends(get_embeddings_service),
    llm: OpenAIChatService = Depends(get_llm_service),
    faiss_repo: FaissRepository = Depends(get_faiss_repo),
    chunks_repo: ChunksRepository = Depends(get_chunks_repo),
) -> ChatService:
    return ChatService(embeddings=embeddings, llm=llm, faiss_repo=faiss_repo, chunks_repo=chunks_repo)

