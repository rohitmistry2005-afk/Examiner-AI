from __future__ import annotations

from dataclasses import dataclass

from app.rag.document_loader import ExtractedPage


@dataclass(frozen=True)
class DocumentChunk:
    content: str
    page_number: int | None
    chunk_index: int


class DocumentChunker:
    def __init__(self, target_chars: int = 1400, overlap_chars: int = 220):
        if target_chars <= overlap_chars:
            raise ValueError("target_chars must be greater than overlap_chars.")
        self.target_chars = target_chars
        self.overlap_chars = overlap_chars

    def chunk_pages(self, pages: list[ExtractedPage]) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []
        index = 0
        for page in pages:
            text = " ".join(page.text.split())
            start = 0
            while start < len(text):
                end = min(len(text), start + self.target_chars)
                if end < len(text):
                    boundary = text.rfind(" ", start, end)
                    if boundary > start + self.target_chars // 2:
                        end = boundary

                content = text[start:end].strip()
                if content:
                    chunks.append(
                        DocumentChunk(
                            content=content,
                            page_number=page.page_number,
                            chunk_index=index,
                        )
                    )
                    index += 1

                if end >= len(text):
                    break
                start = max(0, end - self.overlap_chars)
        return chunks
