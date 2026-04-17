from __future__ import annotations

from dataclasses import dataclass

from openai import OpenAI

from app.core.config import settings


@dataclass(frozen=True)
class LLMResult:
    text: str


class LLMService:
    async def chat(self, *, system: str, user: str) -> LLMResult:
        raise NotImplementedError


class OpenAIChatService(LLMService):
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for OpenAI chat")
        self._client = OpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_chat_model

    async def chat(self, *, system: str, user: str) -> LLMResult:
        resp = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0,
        )
        text = resp.choices[0].message.content or ""
        return LLMResult(text=text)

