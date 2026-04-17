from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.repositories.chunks import ChunksRepository
from app.repositories.faiss import FaissRepository
from app.services.embeddings import EmbeddingsService
from app.services.llm import LLMService


@dataclass(frozen=True)
class ChatAnswer:
    answer: str
    sources: list[tuple[uuid.UUID, float]]


class ChatService:
    def __init__(
        self,
        *,
        embeddings: EmbeddingsService,
        llm: LLMService,
        faiss_repo: FaissRepository,
        chunks_repo: ChunksRepository,
        top_k: int = 5,
    ) -> None:
        self._embeddings = embeddings
        self._llm = llm
        self._faiss = faiss_repo
        self._chunks = chunks_repo
        self._top_k = top_k

    async def chat(self, *, document_id: uuid.UUID, message: str) -> ChatAnswer:
        q = await self._embeddings.embed(message)
        hits = self._faiss.search(document_id=document_id, query_vector=q.vector, top_n=20)
        top = hits[: self._top_k]

        if not top:
            return ChatAnswer(answer="I don't know based on the uploaded documents.", sources=[])

        chunk_ids = [h.chunk_id for h in top]
        chunks = await self._chunks.get_by_ids(chunk_ids)
        chunk_by_id = {c.id: c for c in chunks}

        context_parts: list[str] = []
        sources: list[tuple[uuid.UUID, float]] = []
        for h in top:
            c = chunk_by_id.get(h.chunk_id)
            if not c:
                continue
            context_parts.append(f"[chunk_id={c.id}]\n{c.text}")
            sources.append((c.id, h.score))

        context = "\n\n---\n\n".join(context_parts)
        system = (
            "You are a RAG assistant. Answer ONLY using the provided context.\n"
            "If the context does not contain the answer, say: \"I don't know based on the uploaded documents.\""
        )
        user = f"Context:\n{context}\n\nUser question:\n{message}\n\nAnswer:"

        res = await self._llm.chat(system=system, user=user)
        return ChatAnswer(answer=res.text.strip() or "I don't know based on the uploaded documents.", sources=sources)

