from __future__ import annotations

from uuid import UUID

from app.db.repositories.factory import get_repositories
from app.rag.chunker import DocumentChunker
from app.rag.document_loader import DocumentLoader
from app.rag.embeddings import EmbeddingService
from app.rag.retriever import DocumentRetriever


class DocumentRAGService:
    """Ingest and retrieve user-owned academic documents for examiner grounding."""

    def __init__(
        self,
        repositories: dict | None = None,
        loader: DocumentLoader | None = None,
        chunker: DocumentChunker | None = None,
        embeddings: EmbeddingService | None = None,
    ):
        self.repositories = repositories or get_repositories()
        self.documents = self.repositories["documents"]
        self.loader = loader or DocumentLoader()
        self.chunker = chunker or DocumentChunker()
        self.embeddings = embeddings or EmbeddingService()
        self.retriever = DocumentRetriever(self.repositories, self.embeddings)

    def ingest(
        self,
        *,
        user_id: UUID,
        filename: str,
        mime_type: str,
        data: bytes,
        subject: str | None,
        source_type: str,
    ) -> dict:
        pages = self.loader.load(filename, mime_type, data)
        chunks = self.chunker.chunk_pages(pages)
        if not chunks:
            raise ValueError("No usable text chunks were extracted.")

        # Persist metadata first; chunks remain owned by the same user.
        document = self.documents.create_document({
            "user_id": str(user_id),
            "subject": subject,
            "filename": filename,
            "mime_type": mime_type,
            "source_type": source_type,
            "storage_path": None,
            "status": "processing",
        })

        try:
            vectors = self.embeddings.embed([chunk.content for chunk in chunks])
            payloads = [
                {
                    "document_id": str(document["id"]),
                    "user_id": str(user_id),
                    "content": chunk.content,
                    "page_number": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                    "embedding": vector,
                }
                for chunk, vector in zip(chunks, vectors, strict=True)
            ]
            rows = self.documents.create_chunks(payloads)
            if hasattr(self.documents, "update_document"):
                document = self.documents.update_document(
                    document["id"], user_id, {"status": "ready"}
                )
            else:
                document["status"] = "ready"

            return {
                "document": document,
                "chunks_created": len(rows),
            }
        except Exception:
            if hasattr(self.documents, "update_document"):
                try:
                    self.documents.update_document(
                        document["id"], user_id, {"status": "failed"}
                    )
                except Exception:
                    pass
            raise

    def retrieve_context(
        self,
        *,
        user_id: UUID,
        query: str,
        subject: str | None = None,
        document_id: UUID | None = None,
        match_count: int = 6,
    ) -> list[dict]:
        return self.retriever.retrieve(
            user_id=user_id,
            query=query,
            subject=subject,
            document_id=document_id,
            match_count=match_count,
        )
