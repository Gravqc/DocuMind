from __future__ import annotations

import io

from pypdf import PdfReader

from app.utils.text_extractors.base import ExtractedText, TextExtractor


class PdfExtractor(TextExtractor):
    def supports(self, *, filename: str, content_type: str | None) -> bool:
        return filename.lower().endswith(".pdf") or (content_type or "").lower() == "application/pdf"

    def extract(self, *, data: bytes, filename: str, content_type: str | None) -> ExtractedText:
        reader = PdfReader(io.BytesIO(data))
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        return ExtractedText(text="\n\n".join(pages))

