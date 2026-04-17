from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.api.deps import get_storage
from app.core.config import settings
from app.services.storage.base import StorageService
from app.utils.signing import now_epoch, verify

router = APIRouter(prefix="/storage")


@router.put("/upload/{file_key}")
async def upload_to_local_storage(
    file_key: str,
    request: Request,
    expires: int = Query(...),
    sig: str = Query(..., min_length=64, max_length=64),
    storage: StorageService = Depends(get_storage),
) -> dict:
    if now_epoch() > expires:
        raise HTTPException(status_code=403, detail="Upload URL expired")

    message = f"{file_key}:{expires}"
    if not verify(secret=settings.presign_secret, message=message, signature=sig):
        raise HTTPException(status_code=403, detail="Invalid signature")

    data = await request.body()
    await storage.put_bytes(file_key=file_key, data=data)
    return {"status": "uploaded", "file_key": file_key}

