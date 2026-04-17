from __future__ import annotations

from app.utils.text_extractors.base import ExtractedText, TextExtractor
from app.utils.text_extractors.docx import DocxExtractor
from app.utils.text_extractors.pdf import PdfExtractor
from app.utils.text_extractors.txt import TxtExtractor


class ExtractorRegistry:
    def __init__(self) -> None:
        self._extractors: list[TextExtractor] = [PdfExtractor(), DocxExtractor(), TxtExtractor()]

    def extract(self, *, data: bytes, filename: str, content_type: str | None) -> ExtractedText:
        for ex in self._extractors:
            if ex.supports(filename=filename, content_type=content_type):
                return ex.extract(data=data, filename=filename, content_type=content_type)
        # Fall back to best-effort UTF-8 decode
        return TxtExtractor().extract(data=data, filename=filename, content_type=content_type)

