# DocuMind repo guide

This document explains how the repo is structured, what each subsystem does, and the role of the main technologies (FastAPI, Celery, Alembic, FAISS, etc.).

## Big picture
DocuMind is a **RAG backend**:
- **Ingest**: accept document uploads via an S3-like presigned URL flow.
- **Process asynchronously**: extract text → clean → chunk → embed → index.
- **Serve chat**: embed query → retrieve relevant chunks → prompt LLM with bounded context → return answer + sources.

## Key technologies (what they are, why they’re here)

### FastAPI
- **What it is**: an async Python web framework.
- **How we use it**: defines HTTP endpoints and request/response schemas, and wires dependencies into route handlers.
- **Where to look**: `app/main.py`, `app/api/`.

### PostgreSQL
- **What it is**: relational database.
- **How we use it (V1)**:
  - `documents` table: document metadata + processing status.
  - `chunks` table: chunk text + token counts + embedding vector (kept in DB for V1 debuggability).
- **Where to look**: `app/models/`, `app/repositories/`.

### SQLAlchemy (async)
- **What it is**: ORM + SQL toolkit.
- **How we use it**: async engine/session for repositories and services.
- **Where to look**: `app/db/session.py`, `app/models/`, `app/repositories/`.

### Alembic (migrations)
- **What it is**: schema migration tool for SQLAlchemy.
- **Why it exists**: to evolve the DB schema safely over time, with versioned migrations.
- **How it works here**:
  - `alembic.ini`: Alembic config.
  - `app/db/migrations/env.py`: connects Alembic to our models and DB URL.
  - `app/db/migrations/versions/`: migration scripts.
- **Common commands**:

```bash
poetry run alembic upgrade head
poetry run alembic revision --autogenerate -m "add_something"
```

### Redis
- **What it is**: in-memory data store.
- **How we use it**:
  - broker/backend for Celery.
  - later: caching (embeddings), distributed locks for idempotent processing.
- **Where to look**: `docker-compose.yml`, Celery env vars in `.env.example`.

### Celery (background workers)
- **What it is**: a distributed task queue.
- **Why we need it**: document processing is slow/variable and shouldn’t block HTTP requests.
- **How it works here**:
  - API enqueues a job (e.g. `process_document.delay(document_id)`).
  - Celery worker picks it up from Redis and runs the pipeline.
- **Where to look**: `app/workers/celery_app.py`, `app/workers/tasks.py`.
- **Local test mode**: `CELERY_TASK_ALWAYS_EAGER=1` runs tasks inline (no Redis needed).

### FAISS (vector store)
- **What it is**: a library for fast vector similarity search.
- **How we use it (V1)**:
  - store a per-document FAISS index on disk under `data/faiss/<document_id>/`.
  - keep chunk metadata in Postgres.
- **Where to look**: `app/repositories/faiss.py`.
- **Why per-document indexes**: isolation and simplicity for V1; easier future multi-tenancy.

### OpenAI (embeddings + chat)
- **What it is**: hosted model APIs.
- **How we use it**:
  - embeddings model turns text into vectors.
  - chat model generates grounded answers from retrieved context.
- **Where to look**: `app/services/embeddings.py`, `app/services/llm.py`.
- **Config**: `.env.example` (`OPENAI_API_KEY`, model names).

### tiktoken (token counting)
- **What it is**: tokenizer used by OpenAI models.
- **How we use it**: chunk sizing and overlap are token-based.
- **Important note**: in some locked-down environments, `tiktoken` may try to download encoding data; we include a deterministic offline fallback tokenizer so chunking still works.
- **Where to look**: `app/utils/tokens.py`, `app/services/chunking.py`.

## Directory-by-directory walkthrough

### `app/api/`
HTTP routes and dependency wiring.
- `router.py`: combines route modules.
- `deps.py`: creates/wires services.
- `routes/`:
  - `health.py`: `GET /healthz`
  - `documents.py`: upload-url/confirm/status
  - `storage.py`: local “presigned PUT” endpoint
  - `chat.py`: `POST /chat`

### `app/services/`
Business logic / orchestration.
- `services/storage/*`: storage abstraction (local today, S3 later).
- `documents.py`: confirm + enqueue processing; read status.
- `chunking.py`: structure-aware + sliding-window chunker.
- `embeddings.py`: embeddings provider.
- `llm.py`: LLM provider.
- `chat.py`: retrieval + grounding policy and prompt assembly.

### `app/repositories/`
Persistence and retrieval boundaries.
- `documents.py`, `chunks.py`: DB access.
- `faiss.py`: vector index storage + search.

### `app/models/`
SQLAlchemy ORM models.
- `document.py`: status lifecycle.
- `chunk.py`: chunk text + embedding storage.

### `app/workers/`
Celery configuration + tasks.
- `celery_app.py`: Celery app setup.
- `tasks.py`: worker tasks (pipeline entrypoints).

### `app/utils/`
Utilities that are not “business logic”:
- `text_cleaning.py`: normalization / whitespace cleanup.
- `text_extractors/`: parse files into text (`pdf`, `docx`, `txt`).
- `signing.py`: HMAC signing for local presigned upload URLs.
- `tokens.py`: token counting/encoding with fallback.

## Local “S3-like presigned upload” in one minute
Production pattern:
1. API returns a presigned URL.
2. Client uploads directly to storage.
3. Client confirms upload so backend can process.

Local simulation:
- `POST /documents/upload-url` returns `upload_url` pointing at `PUT /storage/upload/{file_key}` with `expires` + `sig`.
- API validates signature and writes bytes to `data/uploads/`.

## What’s intentionally missing (yet)
- Full `process_document` pipeline implementation (status transitions, retries, idempotency locks, extraction/chunking/embedding/indexing end-to-end).
- Hybrid keyword scoring.
- Auth/multi-tenancy.
- Voice endpoints and streaming chat.

