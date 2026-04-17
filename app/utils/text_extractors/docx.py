from __future__ import annotations

import io

import docx

from app.utils.text_extractors.base import ExtractedText, TextExtractor


class DocxExtractor(TextExtractor):
    def supports(self, *, filename: str, content_type: str | None) -> bool:
        return filename.lower().endswith(".docx") or (content_type or "").lower() in {
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }

    def extract(self, *, data: bytes, filename: str, content_type: str | None) -> ExtractedText:
        document = docx.Document(io.BytesIO(data))
        paragraphs = [p.text for p in document.paragraphs if p.text]
        return ExtractedText(text="\n\n".join(paragraphs))

