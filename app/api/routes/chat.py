from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_chat_service
from app.schemas.chat import ChatRequest, ChatResponse, ChatSource
from app.services.chat import ChatService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, chat_service: ChatService = Depends(get_chat_service)) -> ChatResponse:
    try:
        document_id = uuid.UUID(payload.document_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail="Invalid document_id") from e

    ans = await chat_service.chat(document_id=document_id, message=payload.message)
    return ChatResponse(
        answer=ans.answer,
        sources=[ChatSource(chunk_id=str(cid), score=score) for cid, score in ans.sources],
    )

