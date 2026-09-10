from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from app.db.repositories.base import SupabaseRepository


class ExamRepository(SupabaseRepository):
    table_name = "exam_sessions"

    def create(self, payload: dict) -> dict:
        response = self.client.table(self.table_name).insert(payload).execute()
        return self._require_row(response)

    def get_for_user(self, session_id: UUID, user_id: UUID) -> dict:
        response = (
            self.client.table(self.table_name)
            .select("*")
            .eq("id", self._uuid(session_id))
            .eq("user_id", self._uuid(user_id))
            .single()
            .execute()
        )
        return response.data

    def list_for_user(self, user_id: UUID, limit: int = 50) -> list[dict]:
        response = (
            self.client.table(self.table_name)
            .select("*")
            .eq("user_id", self._uuid(user_id))
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return self._rows(response)

    def update_for_user(self, session_id: UUID, user_id: UUID, payload: dict) -> dict:
        response = (
            self.client.table(self.table_name)
            .update(payload)
            .eq("id", self._uuid(session_id))
            .eq("user_id", self._uuid(user_id))
            .select("*")
            .single()
            .execute()
        )
        return response.data


    def count_questions(self, session_id: UUID) -> int:
        response = (
            self.client.table("questions")
            .select("id", count="exact")
            .eq("exam_session_id", self._uuid(session_id))
            .eq("is_follow_up", False)
            .execute()
        )
        return int(response.count or 0)

    def set_current_question(self, session_id: UUID, user_id: UUID, question_id: UUID) -> dict:
        return self.update_for_user(
            session_id,
            user_id,
            {"current_question_id": str(question_id)},
        )

    def clear_current_question(self, session_id: UUID, user_id: UUID) -> dict:
        return self.update_for_user(
            session_id,
            user_id,
            {"current_question_id": None},
        )

    def start(self, session_id: UUID, user_id: UUID) -> dict:
        return self.update_for_user(
            session_id,
            user_id,
            {
                "status": "in_progress",
                "started_at": datetime.now(timezone.utc).isoformat(),
            },
        )

    def complete(self, session_id: UUID, user_id: UUID) -> dict:
        return self.update_for_user(
            session_id,
            user_id,
            {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "current_question_id": None,
            },
        )
