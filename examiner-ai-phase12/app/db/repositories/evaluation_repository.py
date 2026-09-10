from uuid import UUID

from app.db.repositories.base import SupabaseRepository


class EvaluationRepository(SupabaseRepository):
    table_name = "evaluations"

    def create(self, payload: dict) -> dict:
        response = self.client.table(self.table_name).insert(payload).execute()
        return self._require_row(response)

    def get_for_answer(self, answer_id: UUID) -> dict | None:
        response = (
            self.client.table(self.table_name)
            .select("*")
            .eq("answer_id", self._uuid(answer_id))
            .limit(1)
            .execute()
        )
        rows = self._rows(response)
        return rows[0] if rows else None

    def list_for_answer_ids(self, answer_ids: list[UUID]) -> list[dict]:
        if not answer_ids:
            return []
        response = (
            self.client.table(self.table_name)
            .select("*")
            .in_("answer_id", [self._uuid(value) for value in answer_ids])
            .order("created_at")
            .execute()
        )
        return self._rows(response)
