from uuid import UUID

from app.db.repositories.base import SupabaseRepository


class PerformanceRepository(SupabaseRepository):
    table_name = "topic_performance"

    def upsert(self, payload: dict) -> dict:
        response = (
            self.client.table(self.table_name)
            .upsert(payload, on_conflict="exam_session_id,topic")
            .select("*")
            .single()
            .execute()
        )
        return response.data

    def list_for_session(self, session_id: UUID) -> list[dict]:
        response = (
            self.client.table(self.table_name)
            .select("*")
            .eq("exam_session_id", self._uuid(session_id))
            .order("topic")
            .execute()
        )
        return self._rows(response)
