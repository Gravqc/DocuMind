from __future__ import annotations

from app.utils.text_extractors.base import ExtractedText, TextExtractor


class TxtExtractor(TextExtractor):
    def supports(self, *, filename: str, content_type: str | None) -> bool:
        return filename.lower().endswith(".txt") or (content_type or "").lower().startswith("text/")

    def extract(self, *, data: bytes, filename: str, content_type: str | None) -> ExtractedText:
        text = data.decode("utf-8", errors="replace")
        return ExtractedText(text=text)

