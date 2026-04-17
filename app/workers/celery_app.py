from __future__ import annotations

import os

from celery import Celery


def make_celery() -> Celery:
    broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    result_backend = os.getenv("CELERY_RESULT_BACKEND", broker_url)

    celery = Celery("documind", broker=broker_url, backend=result_backend, include=["app.workers.tasks"])

    celery.conf.update(
        task_acks_late=True,
        worker_prefetch_multiplier=1,
        task_default_retry_delay=10,
        task_routes={"app.workers.tasks.process_document": {"queue": "documents"}},
    )

    if os.getenv("CELERY_TASK_ALWAYS_EAGER", "0") == "1":
        celery.conf.task_always_eager = True
        celery.conf.task_eager_propagates = True

    return celery


celery_app = make_celery()

