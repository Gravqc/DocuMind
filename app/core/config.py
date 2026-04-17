from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "DocuMind"
    environment: str = os.getenv("ENVIRONMENT", "local")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://documind:documind@localhost:5432/documind",
    )
    presign_secret: str = os.getenv("PRESIGN_SECRET", "dev-only-change-me")
    data_dir: str = os.getenv("DATA_DIR", "data")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_embeddings_model: str = os.getenv("OPENAI_EMBEDDINGS_MODEL", "text-embedding-3-small")
    openai_chat_model: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")


settings = Settings()

