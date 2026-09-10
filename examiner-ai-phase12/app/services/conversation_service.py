from __future__ import annotations

from uuid import UUID

from app.db.repositories.factory import get_repositories
from app.schemas.domain import ChatTurnResponse, EvaluationRecord, QuestionRecord
from app.services.adaptive_service import AdaptiveEngine
from app.services.evaluation_service import EvaluationService
from app.services.followup_service import FollowUpService
from app.services.question_service import QuestionService


class ConversationService:
    """One conversational examination turn: answer -> evaluate -> probe/advance."""

    def __init__(
        self,
        repositories: dict | None = None,
        evaluation_service: EvaluationService | None = None,
        question_service: QuestionService | None = None,
        adaptive_engine: AdaptiveEngine | None = None,
        followup_service: FollowUpService | None = None,
    ):
        self.repositories = repositories or get_repositories()
        self.exams = self.repositories["exams"]
        self.questions = self.repositories["questions"]
        self.evaluation_service = evaluation_service or EvaluationService(self.repositories)
        self.question_service = question_service or QuestionService(self.repositories)
        self.adaptive_engine = adaptive_engine or AdaptiveEngine(self.repositories)
        self.followup_service = followup_service or FollowUpService(self.repositories)

    @staticmethod
    def _feedback(evaluation: EvaluationRecord) -> str:
        text = evaluation.feedback.strip()
        if evaluation.missing_concepts:
            text += " Key area to strengthen: " + ", ".join(evaluation.missing_concepts[:3]) + "."
        return text

    @staticmethod
    def _transition(action: str) -> str:
        return {
            "advance": "Let's move to the next topic.",
            "reinforce": "Let's reinforce this area with another question.",
            "increase_difficulty": "You've demonstrated strong understanding, so I'll raise the difficulty.",
            "decrease_difficulty": "Let's reinforce the concept at a slightly easier level.",
            "maintain": "Let's continue at the current level.",
        }.get(action, "Let's continue.")

    def submit_turn(
        self,
        user_id: UUID,
        session_id: UUID,
        question_id: UUID,
        answer_text: str,
    ) -> ChatTurnResponse:
        # Capture the answered question before Phase 5 marks it as answered
        # and clears the current-question pointer.
        question_row = self.questions.get_for_session(question_id, session_id)
        if not question_row:
            raise LookupError("Question not found in this exam session.")
        parent_question = QuestionRecord.model_validate(question_row)

        answer, evaluation = self.evaluation_service.submit_answer(
            user_id=user_id,
            session_id=session_id,
            question_id=question_id,
            answer_text=answer_text,
        )

        decision = self.adaptive_engine.select_next(user_id, session_id)

        # Phase 8: probe the student's demonstrated gap before advancing.
        follow_up = self.followup_service.create_follow_up(
            user_id=user_id,
            session_id=session_id,
            parent_question=parent_question,
            answer_text=answer_text,
            evaluation=evaluation,
        )

        if follow_up is not None:
            return ChatTurnResponse(
                examiner_message=(
                    f"{self._feedback(evaluation)} "
                    "I want to probe that point a little further. "
                    f"{follow_up.question_text}"
                ).strip(),
                answer=answer,
                evaluation=evaluation,
                adaptive_decision=decision,
                next_question=follow_up,
                exam_completed=False,
            )

        session_row = self.exams.get_for_user(session_id, user_id)
        main_count = self.exams.count_questions(session_id)
        configured_count = int(session_row["question_count"])

        if main_count >= configured_count:
            return ChatTurnResponse(
                examiner_message=(
                    f"{self._feedback(evaluation)} "
                    "That completes the configured examination. "
                    "Finish the exam to view your performance report."
                ).strip(),
                answer=answer,
                evaluation=evaluation,
                adaptive_decision=decision,
                next_question=None,
                exam_completed=True,
            )

        next_question = self.question_service.generate_next_main_question(
            user_id, session_id
        )

        return ChatTurnResponse(
            examiner_message=(
                f"{self._feedback(evaluation)} "
                f"{self._transition(decision.action)} "
                f"{next_question.question_text}"
            ).strip(),
            answer=answer,
            evaluation=evaluation,
            adaptive_decision=decision,
            next_question=next_question,
            exam_completed=False,
        )
