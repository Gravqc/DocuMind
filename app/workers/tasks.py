from __future__ import annotations

import logging
import uuid

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_jitter=True, max_retries=5)
def process_document(self, document_id: str) -> None:
    """
    V1 placeholder.

    This will become the full pipeline (fetch→extract→clean→chunk→embed→index) once
    storage + extractors + embeddings + FAISS are wired.
    """
    _ = uuid.UUID(document_id)
    logger.info("process_document started", extra={"document_id": document_id, "task_id": self.request.id})

