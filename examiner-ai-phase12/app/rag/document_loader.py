from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import fitz
from docx import Document


SUPPORTED_MIME_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
}

SUPPORTED_EXTENSIONS = {".pdf": "pdf", ".docx": "docx"}


@dataclass(frozen=True)
class ExtractedPage:
    text: str
    page_number: int


class DocumentExtractionError(ValueError):
    pass


class DocumentLoader:
    MAX_BYTES = 10 * 1024 * 1024

    def load(self, filename: str, mime_type: str, data: bytes) -> list[ExtractedPage]:
        if len(data) > self.MAX_BYTES:
            raise DocumentExtractionError("Document exceeds the 10 MB upload limit.")

        kind = SUPPORTED_MIME_TYPES.get(mime_type) or SUPPORTED_EXTENSIONS.get(
            Path(filename).suffix.lower()
        )
        if kind == "pdf":
            return self._pdf(data)
        if kind == "docx":
            return self._docx(data)
        raise DocumentExtractionError("Only PDF and DOCX documents are supported.")

    @staticmethod
    def _pdf(data: bytes) -> list[ExtractedPage]:
        try:
            document = fitz.open(stream=data, filetype="pdf")
        except Exception as exc:
            raise DocumentExtractionError("Unable to read the PDF document.") from exc

        pages: list[ExtractedPage] = []
        for index, page in enumerate(document, start=1):
            text = " ".join(page.get_text("text").split())
            if text:
                pages.append(ExtractedPage(text=text, page_number=index))
        if not pages:
            raise DocumentExtractionError("The PDF contains no extractable text.")
        return pages

    @staticmethod
    def _docx(data: bytes) -> list[ExtractedPage]:
        try:
            document = Document(BytesIO(data))
        except Exception as exc:
            raise DocumentExtractionError("Unable to read the DOCX document.") from exc

        paragraphs = [
            " ".join(p.text.split())
            for p in document.paragraphs
            if p.text and p.text.strip()
        ]
        text = "\n".join(paragraphs)
        if not text:
            raise DocumentExtractionError("The DOCX contains no extractable text.")
        return [ExtractedPage(text=text, page_number=1)]
