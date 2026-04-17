from __future__ import annotations

from dataclasses import dataclass

from app.utils.tokens import decode, encode


@dataclass(frozen=True)
class Chunk:
    index: int
    text: str
    token_count: int


def _split_structure(text: str) -> list[str]:
    # Structure-aware split: paragraphs/sections separated by blank lines.
    # Keep non-empty blocks.
    blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
    return blocks or [text]


def chunk_text(
    text: str,
    *,
    model: str = "gpt-4o-mini",
    min_tokens: int = 300,
    max_tokens: int = 800,
    overlap_tokens: int = 80,
) -> list[Chunk]:
    if max_tokens <= 0 or overlap_tokens < 0 or min_tokens <= 0:
        raise ValueError("Invalid chunking parameters")
    if overlap_tokens >= max_tokens:
        raise ValueError("overlap_tokens must be < max_tokens")

    blocks = _split_structure(text)
    tokens: list[int] = []
    for i, b in enumerate(blocks):
        if i:
            tokens.extend(encode("\n\n", model=model))
        tokens.extend(encode(b, model=model))

    chunks: list[Chunk] = []
    start = 0
    idx = 0
    step = max_tokens - overlap_tokens

    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        window = tokens[start:end]
        # If we're near the end and the final chunk is too small, merge it into previous.
        if chunks and (len(window) < min_tokens) and end == len(tokens):
            prev = chunks[-1]
            merged_tokens = encode(prev.text, model=model) + window
            merged_text = decode(merged_tokens, model=model)
            chunks[-1] = Chunk(index=prev.index, text=merged_text, token_count=len(merged_tokens))
            break

        chunk_text_str = decode(window, model=model)
        chunks.append(Chunk(index=idx, text=chunk_text_str, token_count=len(window)))
        idx += 1
        start += step

    return chunks

