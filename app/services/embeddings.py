from __future__ import annotations

from dataclasses import dataclass

from openai import OpenAI

from app.core.config import settings


@dataclass(frozen=True)
class EmbeddingResult:
    vector: list[float]


class EmbeddingsService:
    async def embed(self, text: str) -> EmbeddingResult:
        raise NotImplementedError


class OpenAIEmbeddingsService(EmbeddingsService):
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for OpenAI embeddings")
        self._client = OpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_embeddings_model

    async def embed(self, text: str) -> EmbeddingResult:
        # OpenAI Python SDK is sync; keep interface async for future non-blocking impl.
        resp = self._client.embeddings.create(model=self._model, input=text)
        return EmbeddingResult(vector=list(resp.data[0].embedding))

