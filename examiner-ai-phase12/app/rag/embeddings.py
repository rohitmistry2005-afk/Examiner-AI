from __future__ import annotations

from app.ai.gemini_client import GeminiClient


class EmbeddingService:
    def __init__(self, gemini: GeminiClient | None = None, dimension: int = 768):
        self.gemini = gemini or GeminiClient()
        self.dimension = dimension

    def embed(self, texts: list[str], batch_size: int = 16) -> list[list[float]]:
        vectors: list[list[float]] = []
        for start in range(0, len(texts), batch_size):
            vectors.extend(
                self.gemini.embed_texts(
                    texts[start:start + batch_size],
                    output_dimensionality=self.dimension,
                )
            )
        return vectors
