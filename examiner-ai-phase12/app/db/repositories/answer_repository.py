from uuid import UUID

from app.db.repositories.base import SupabaseRepository


class AnswerRepository(SupabaseRepository):
    table_name = "answers"

    def create(self, payload: dict) -> dict:
        response = self.client.table(self.table_name).insert(payload).execute()
        return self._require_row(response)

    def get_for_question_and_user(self, question_id: UUID, user_id: UUID) -> dict | None:
        response = (
            self.client.table(self.table_name)
            .select("*")
            .eq("question_id", self._uuid(question_id))
            .eq("user_id", self._uuid(user_id))
            .limit(1)
            .execute()
        )
        rows = self._rows(response)
        return rows[0] if rows else None

    def list_for_question(self, question_id: UUID) -> list[dict]:
        response = (
            self.client.table(self.table_name)
            .select("*")
            .eq("question_id", self._uuid(question_id))
            .order("submitted_at")
            .execute()
        )
        return self._rows(response)

    def list_for_session(self, session_id: UUID) -> list[dict]:
        response = (
            self.client.table(self.table_name)
            .select("*")
            .eq("exam_session_id", self._uuid(session_id))
            .order("submitted_at")
            .execute()
        )
        return self._rows(response)
