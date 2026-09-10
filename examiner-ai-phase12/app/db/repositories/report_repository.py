from uuid import UUID

from app.db.repositories.base import SupabaseRepository


class ReportRepository(SupabaseRepository):
    table_name = "reports"

    def get_for_session(self, session_id: UUID, user_id: UUID) -> dict | None:
        response = (
            self.client.table(self.table_name)
            .select("*")
            .eq("exam_session_id", self._uuid(session_id))
            .eq("user_id", self._uuid(user_id))
            .limit(1)
            .execute()
        )
        rows = self._rows(response)
        return rows[0] if rows else None

    def upsert(self, payload: dict) -> dict:
        response = (
            self.client.table(self.table_name)
            .upsert(payload, on_conflict="exam_session_id")
            .select("*")
            .single()
            .execute()
        )
        return response.data
