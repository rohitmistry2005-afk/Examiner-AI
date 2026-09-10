
from __future__ import annotations

from uuid import UUID

from app.db.repositories.factory import get_repositories
from app.schemas.ai import AdaptiveDecisionResult
from app.schemas.domain import (
    ExamSessionRecord,
    KnowledgeStateRecord,
    QuestionRecord,
    TopicPerformanceRecord,
)


class AdaptiveEngine:
    """Deterministic controller for the next conversational examiner turn."""

    def __init__(self, repositories: dict | None = None):
        self.repositories = repositories or get_repositories()
        self.exams = self.repositories["exams"]
        self.questions = self.repositories["questions"]
        self.knowledge = self.repositories.get("knowledge")
        self.performance = self.repositories.get("performance")

    @staticmethod
    def _key(value: str) -> str:
        return " ".join(str(value).split()).casefold()

    @staticmethod
    def _clamp(value: int) -> int:
        return max(1, min(5, int(value)))

    def _answered_main_questions(self, session_id: UUID) -> list[QuestionRecord]:
        rows = self.questions.list_for_session(session_id)
        return [
            QuestionRecord.model_validate(row)
            for row in rows
            if not row.get("is_follow_up", False)
            and row.get("status") == "answered"
        ]

    def _maps(self, session_id: UUID):
        knowledge = {
            self._key(row["topic"]): KnowledgeStateRecord.model_validate(row)
            for row in self.knowledge.list_for_session(session_id)
        }
        performance = {
            self._key(row["topic"]): TopicPerformanceRecord.model_validate(row)
            for row in self.performance.list_for_session(session_id)
        }
        return knowledge, performance

    def select_next(self, user_id: UUID, session_id: UUID) -> AdaptiveDecisionResult:
        session_row = self.exams.get_for_user(session_id, user_id)
        if not session_row:
            raise LookupError("Exam session not found.")

        # Preserve earlier phase test doubles that intentionally do not include
        # knowledge/performance repositories.
        if self.knowledge is None or self.performance is None:
            topics = list(session_row.get("topics") or [])
            if not topics:
                raise ValueError("The exam has no configured topics.")
            if session_row.get("status") != "in_progress":
                raise ValueError("Adaptive decisions require an in-progress exam.")
            answered = self._answered_main_questions(session_id)
            return AdaptiveDecisionResult(
                action="advance",
                target_topic=topics[len(answered) % len(topics)],
                difficulty=int(session_row.get("initial_difficulty", 3)),
                reason="Adaptive state unavailable; preserve configured topic rotation.",
            )

        session = ExamSessionRecord.model_validate(session_row)
        if not session.topics:
            raise ValueError("The exam has no configured topics.")
        if session.status.value != "in_progress":
            raise ValueError("Adaptive decisions require an in-progress exam.")

        knowledge, performance = self._maps(session_id)
        answered = self._answered_main_questions(session_id)
        covered = {self._key(q.topic) for q in answered}

        # First cover every configured topic once.
        uncovered = [
            topic for topic in session.topics
            if self._key(topic) not in covered
        ]
        if uncovered:
            return AdaptiveDecisionResult(
                action="advance",
                target_topic=uncovered[0],
                difficulty=session.initial_difficulty,
                reason="Uncovered configured topic prioritized for syllabus coverage.",
            )

        last_topic = self._key(answered[-1].topic) if answered else None

        def rank(topic: str):
            state = knowledge.get(self._key(topic))
            perf = performance.get(self._key(topic))
            mastery = state.mastery_score if state else 0.0
            accuracy = perf.accuracy if perf else 0.0
            attempts = perf.questions_attempted if perf else 0
            same_as_last = 1 if self._key(topic) == last_topic and len(session.topics) > 1 else 0
            return (mastery, accuracy, attempts, same_as_last)

        target = min(session.topics, key=rank)
        state = knowledge.get(self._key(target))

        if state is None:
            return AdaptiveDecisionResult(
                action="advance",
                target_topic=target,
                difficulty=session.initial_difficulty,
                reason="Topic has no knowledge evidence yet.",
            )

        current = self._clamp(state.current_difficulty)
        if state.mastery_score < 0.35:
            return AdaptiveDecisionResult(
                action="decrease_difficulty",
                target_topic=target,
                difficulty=self._clamp(current - 1),
                reason="Low mastery detected; reinforce at a lower difficulty.",
            )
        if state.mastery_score >= 0.80:
            return AdaptiveDecisionResult(
                action="increase_difficulty",
                target_topic=target,
                difficulty=self._clamp(current + 1),
                reason="Strong mastery detected; test deeper understanding.",
            )
        return AdaptiveDecisionResult(
            action="maintain",
            target_topic=target,
            difficulty=current,
            reason="Moderate mastery detected; maintain the current challenge.",
        )
