from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)
    document_id: str = Field(..., min_length=1)


class ChatSource(BaseModel):
    chunk_id: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource]

