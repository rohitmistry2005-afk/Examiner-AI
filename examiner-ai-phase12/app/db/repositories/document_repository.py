from uuid import UUID

from app.db.repositories.base import SupabaseRepository


class DocumentRepository(SupabaseRepository):
    def create_document(self, payload: dict) -> dict:
        response = self.client.table("documents").insert(payload).execute()
        return self._require_row(response)

    def create_chunks(self, payloads: list[dict]) -> list[dict]:
        if not payloads:
            return []
        response = self.client.table("document_chunks").insert(payloads).execute()
        return self._rows(response)

    def list_for_user(self, user_id: UUID) -> list[dict]:
        response = (
            self.client.table("documents")
            .select("*")
            .eq("user_id", self._uuid(user_id))
            .order("created_at", desc=True)
            .execute()
        )
        return self._rows(response)

    def match_chunks(self, *, user_id: UUID, embedding: list[float], match_count: int = 8,
                     document_id: UUID | None = None, subject: str | None = None) -> list[dict]:
        params = {
            "query_embedding": embedding,
            "match_threshold": 0.5,
            "match_count": match_count,
            "filter_user_id": self._uuid(user_id),
            "filter_document_id": self._uuid(document_id) if document_id else None,
            "filter_subject": subject,
        }
        response = self.client.rpc("match_document_chunks", params).execute()
        return self._rows(response)

    def update_document(self, document_id: UUID, user_id: UUID, payload: dict) -> dict:
        response = (
            self.client.table("documents")
            .update(payload)
            .eq("id", self._uuid(document_id))
            .eq("user_id", self._uuid(user_id))
            .select("*")
            .single()
            .execute()
        )
        return response.data

