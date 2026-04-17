from __future__ import annotations

import re
from typing import Any


_WORD_RE = re.compile(r"\S+")


def _try_tiktoken() -> Any | None:
    try:
        import tiktoken  # type: ignore

        return tiktoken
    except Exception:
        return None


def _tiktoken_encoding(model: str) -> Any | None:
    tiktoken = _try_tiktoken()
    if not tiktoken:
        return None
    try:
        return tiktoken.encoding_for_model(model)
    except Exception:
        # Avoid encodings that may require network fetch in constrained environments.
        for enc_name in ("gpt2", "cl100k_base"):
            try:
                return tiktoken.get_encoding(enc_name)
            except Exception:
                continue
    return None


def count_tokens(text: str, *, model: str = "gpt-4o-mini") -> int:
    enc = _tiktoken_encoding(model)
    if enc is not None:
        return len(enc.encode(text))
    return len(_WORD_RE.findall(text))


def encode(text: str, *, model: str = "gpt-4o-mini") -> list[Any]:
    enc = _tiktoken_encoding(model)
    if enc is not None:
        return enc.encode(text)
    # Fallback tokenization: whitespace tokens. Good enough for deterministic windowing offline.
    return _WORD_RE.findall(text)


def decode(tokens: list[Any], *, model: str = "gpt-4o-mini") -> str:
    enc = _tiktoken_encoding(model)
    if enc is not None and tokens and isinstance(tokens[0], int):
        return enc.decode(tokens)
    return " ".join(str(t) for t in tokens)

