from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractedText:
    text: str


class TextExtractor:
    def supports(self, *, filename: str, content_type: str | None) -> bool:
        raise NotImplementedError

    def extract(self, *, data: bytes, filename: str, content_type: str | None) -> ExtractedText:
        raise NotImplementedError

