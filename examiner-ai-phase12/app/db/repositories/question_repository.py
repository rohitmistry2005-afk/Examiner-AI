from uuid import UUID

from app.db.repositories.base import SupabaseRepository


class QuestionRepository(SupabaseRepository):
    table_name = "questions"

    def create(self, payload: dict) -> dict:
        response = self.client.table(self.table_name).insert(payload).execute()
        return self._require_row(response)

    def get_for_session(self, question_id: UUID, session_id: UUID) -> dict:
        response = (
            self.client.table(self.table_name)
            .select("*")
            .eq("id", self._uuid(question_id))
            .eq("exam_session_id", self._uuid(session_id))
            .single()
            .execute()
        )
        return response.data

    def get_current(self, session_id: UUID) -> dict | None:
        response = (
            self.client.table(self.table_name)
            .select("*")
            .eq("exam_session_id", self._uuid(session_id))
            .eq("status", "asked")
            .order("sequence_number", desc=True)
            .limit(1)
            .execute()
        )
        rows = self._rows(response)
        return rows[0] if rows else None

    def list_for_session(self, session_id: UUID) -> list[dict]:
        response = (
            self.client.table(self.table_name)
            .select("*")
            .eq("exam_session_id", self._uuid(session_id))
            .order("sequence_number")
            .execute()
        )
        return self._rows(response)

    def mark_asked(self, question_id: UUID, session_id: UUID) -> dict:
        response = (
            self.client.table(self.table_name)
            .update({"status": "asked"})
            .eq("id", self._uuid(question_id))
            .eq("exam_session_id", self._uuid(session_id))
            .select("*")
            .single()
            .execute()
        )
        return response.data


    def get_latest_sequence(self, session_id: UUID) -> int:
        response = (
            self.client.table(self.table_name)
            .select("sequence_number")
            .eq("exam_session_id", self._uuid(session_id))
            .order("sequence_number", desc=True)
            .limit(1)
            .execute()
        )
        rows = self._rows(response)
        return int(rows[0]["sequence_number"]) if rows else 0

    def mark_answered(self, question_id: UUID, session_id: UUID) -> dict:
        response = (
            self.client.table(self.table_name)
            .update({"status": "answered"})
            .eq("id", self._uuid(question_id))
            .eq("exam_session_id", self._uuid(session_id))
            .select("*")
            .single()
            .execute()
        )
        return response.data

    def create_and_ask(self, payload: dict) -> dict:
        # Kept as a simple repository operation; transactionality belongs
        # to the database migration if/when atomic RPCs are introduced.
        row = self.create(payload)
        return self.mark_asked(UUID(row["id"]), UUID(row["exam_session_id"]))
