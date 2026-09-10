from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from app.db.repositories.factory import get_repositories
from app.schemas.domain import EvaluationRecord, KnowledgeStateRecord, TopicPerformanceRecord


class KnowledgeStateService:
    """Update persistent topic mastery/evidence after a validated evaluation."""

    def __init__(self, repositories: dict | None = None):
        self.repositories = repositories or get_repositories()
        self.exams = self.repositories["exams"]
        self.knowledge = self.repositories["knowledge"]
        self.performance = self.repositories["performance"]

    @staticmethod
    def _evidence(evaluation: EvaluationRecord) -> float:
        # A bounded semantic evidence score derived from the evaluation dimensions.
        return round(
            (
                evaluation.correctness * 0.45
                + evaluation.completeness * 0.30
                + evaluation.conceptual_understanding * 0.25
            ),
            4,
        )

    @staticmethod
    def _dedupe(values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            cleaned = " ".join(str(value).split())
            key = cleaned.casefold()
            if cleaned and key not in seen:
                seen.add(key)
                result.append(cleaned)
        return result

    @staticmethod
    def _remove_case_insensitive(source: list[str], remove: list[str]) -> list[str]:
        remove_keys = {" ".join(str(v).split()).casefold() for v in remove if str(v).strip()}
        return [v for v in source if str(v).casefold() not in remove_keys]

    @staticmethod
    def _difficulty_from_mastery(mastery: float, previous: int) -> int:
        # Phase 6 stores a bounded current difficulty estimate. Phase 7 owns
        # the actual next-question decision policy.
        if mastery >= 0.80:
            return min(5, max(previous, 4))
        if mastery >= 0.60:
            return min(5, max(previous, 3))
        if mastery < 0.35:
            return max(1, min(previous, 2))
        return previous

    def update_after_evaluation(
        self,
        user_id: UUID,
        session_id: UUID,
        topic: str,
        evaluation: EvaluationRecord,
        question_difficulty: int,
    ) -> KnowledgeStateRecord:
        if not topic.strip():
            raise ValueError("Topic is required to update knowledge state.")

        existing_rows = self.knowledge.list_for_session(session_id)
        existing = next(
            (row for row in existing_rows if str(row.get("topic", "")).casefold() == topic.casefold()),
            None,
        )

        prior_attempts = int(existing.get("attempts", 0)) if existing else 0
        prior_mastery = float(existing.get("mastery_score", 0.0)) if existing else 0.0

        evidence = self._evidence(evaluation)
        total_attempts = prior_attempts + 1
        mastery = round(
            ((prior_mastery * prior_attempts) + evidence) / total_attempts,
            4,
        )

        old_strong = list(existing.get("strong_concepts", [])) if existing else []
        old_weak = list(existing.get("weak_concepts", [])) if existing else []
        old_misconceptions = list(existing.get("misconceptions", [])) if existing else []

        missing = self._dedupe(evaluation.missing_concepts)
        misconceptions = self._dedupe(evaluation.misconceptions)
        strengths = self._dedupe(evaluation.strengths)

        strong = self._dedupe(old_strong + strengths)
        weak = self._dedupe(old_weak + missing + misconceptions)

        # Evidence of mastery resolves concepts previously marked weak.
        strong_keys = {v.casefold() for v in strong}
        weak = [v for v in weak if v.casefold() not in strong_keys]

        all_misconceptions = self._dedupe(old_misconceptions + misconceptions)
        difficulty = self._difficulty_from_mastery(
            mastery,
            int(existing.get("current_difficulty", question_difficulty)) if existing else question_difficulty,
        )

        payload = {
            "user_id": str(user_id),
            "exam_session_id": str(session_id),
            "topic": topic.strip(),
            "mastery_score": mastery,
            "current_difficulty": difficulty,
            "strong_concepts": strong,
            "weak_concepts": weak,
            "misconceptions": all_misconceptions,
            "attempts": total_attempts,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        row = self.knowledge.upsert(payload)
        return KnowledgeStateRecord.model_validate(row)

    def update_topic_performance(
        self,
        user_id: UUID,
        session_id: UUID,
        topic: str,
        evaluation: EvaluationRecord,
    ) -> TopicPerformanceRecord:
        existing_rows = self.performance.list_for_session(session_id)
        existing = next(
            (row for row in existing_rows if str(row.get("topic", "")).casefold() == topic.casefold()),
            None,
        )

        attempts = int(existing.get("questions_attempted", 0)) if existing else 0
        old_average = float(existing.get("average_score", 0.0)) if existing else 0.0
        old_accuracy = float(existing.get("accuracy", 0.0)) if existing else 0.0

        new_attempts = attempts + 1
        average_score = round(
            ((old_average * attempts) + evaluation.score) / new_attempts,
            2,
        )
        accuracy = round(
            ((old_accuracy * attempts) + evaluation.correctness) / new_attempts,
            4,
        )

        payload = {
            "user_id": str(user_id),
            "exam_session_id": str(session_id),
            "topic": topic.strip(),
            "questions_attempted": new_attempts,
            "average_score": average_score,
            "accuracy": accuracy,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        row = self.performance.upsert(payload)
        return TopicPerformanceRecord.model_validate(row)

    def process_evaluation(
        self,
        user_id: UUID,
        session_id: UUID,
        topic: str,
        evaluation: EvaluationRecord,
        question_difficulty: int,
    ) -> tuple[KnowledgeStateRecord, TopicPerformanceRecord]:
        knowledge_state = self.update_after_evaluation(
            user_id=user_id,
            session_id=session_id,
            topic=topic,
            evaluation=evaluation,
            question_difficulty=question_difficulty,
        )
        performance = self.update_topic_performance(
            user_id=user_id,
            session_id=session_id,
            topic=topic,
            evaluation=evaluation,
        )
        return knowledge_state, performance

    def list_knowledge_states(
        self,
        user_id: UUID,
        session_id: UUID,
    ) -> list[KnowledgeStateRecord]:
        session = self.exams.get_for_user(session_id, user_id)
        if not session:
            raise LookupError("Exam session not found.")
        return [
            KnowledgeStateRecord.model_validate(row)
            for row in self.knowledge.list_for_session(session_id)
        ]

    def list_topic_performance(
        self,
        user_id: UUID,
        session_id: UUID,
    ) -> list[TopicPerformanceRecord]:
        session = self.exams.get_for_user(session_id, user_id)
        if not session:
            raise LookupError("Exam session not found.")
        return [
            TopicPerformanceRecord.model_validate(row)
            for row in self.performance.list_for_session(session_id)
        ]
