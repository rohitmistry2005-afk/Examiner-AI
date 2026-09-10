from __future__ import annotations

from uuid import UUID

from app.db.repositories.factory import get_repositories
from app.rag.embeddings import EmbeddingService


class DocumentRetriever:
    def __init__(
        self,
        repositories: dict | None = None,
        embeddings: EmbeddingService | None = None,
    ):
        self.repositories = repositories or get_repositories()
        self.documents = self.repositories["documents"]
        self.embeddings = embeddings or EmbeddingService()

    def retrieve(
        self,
        *,
        user_id: UUID,
        query: str,
        subject: str | None = None,
        document_id: UUID | None = None,
        match_count: int = 6,
    ) -> list[dict]:
        if not query.strip():
            return []
        if hasattr(self.documents, "list_for_user"):
            documents = self.documents.list_for_user(user_id)
            if document_id is not None:
                documents = [
                    row for row in documents if str(row.get("id")) == str(document_id)
                ]
            if subject:
                documents = [
                    row for row in documents
                    if row.get("subject") in (None, subject)
                ]
            if not documents:
                return []

        [embedding] = self.embeddings.embed([query])
        return self.documents.match_chunks(
            user_id=user_id,
            embedding=embedding,
            match_count=match_count,
            document_id=document_id,
            subject=subject,
        )
