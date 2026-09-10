from __future__ import annotations

from uuid import UUID

from app.ai.gemini_client import GeminiClient
from app.ai.prompts.followup import build_followup_prompt
from app.ai.prompts.question import validate_generated_question
from app.db.repositories.factory import get_repositories
from app.models.enums import QuestionStatus, QuestionType
from app.schemas.ai import QuestionGenerationResult
from app.schemas.domain import EvaluationRecord, QuestionRecord
from app.rag.document_rag import DocumentRAGService
from app.rag.context import format_retrieved_context
from app.rag.web_rag import WebRAGService


class FollowUpService:
    MAX_FOLLOWUPS_PER_QUESTION = 2
    SCORE_THRESHOLD = 6.0
    COMPLETENESS_THRESHOLD = 0.60
    CONCEPT_THRESHOLD = 0.60

    def __init__(self, repositories: dict | None = None, gemini: GeminiClient | None = None):
        self.repositories = repositories or get_repositories()
        self.exams = self.repositories["exams"]
        self.questions = self.repositories["questions"]
        self.gemini = gemini or GeminiClient()
        self.document_rag = DocumentRAGService(self.repositories) if "documents" in self.repositories else None
        self.web_rag = WebRAGService(self.gemini)

    @classmethod
    def should_follow_up(cls, evaluation: EvaluationRecord) -> bool:
        return bool(
            evaluation.misconceptions
            or evaluation.missing_concepts
            or evaluation.score < cls.SCORE_THRESHOLD
            or evaluation.completeness < cls.COMPLETENESS_THRESHOLD
            or evaluation.conceptual_understanding < cls.CONCEPT_THRESHOLD
        )

    def _followups(self, session_id: UUID, parent_question_id: UUID) -> list[dict]:
        return [
            row
            for row in self.questions.list_for_session(session_id)
            if row.get("is_follow_up")
            and str(row.get("parent_question_id")) == str(parent_question_id)
        ]

    def create_follow_up(
        self,
        user_id: UUID,
        session_id: UUID,
        parent_question: QuestionRecord,
        answer_text: str,
        evaluation: EvaluationRecord,
    ) -> QuestionRecord | None:
        if not self.should_follow_up(evaluation):
            return None

        existing = self._followups(session_id, parent_question.id)
        if len(existing) >= self.MAX_FOLLOWUPS_PER_QUESTION:
            return None

        session = self.exams.get_for_user(session_id, user_id)
        if not session:
            raise LookupError("Exam session not found.")
        if session["status"] != "in_progress":
            raise ValueError("Follow-ups require an in-progress exam.")

        number = len(existing) + 1
        difficulty = max(1, min(5, parent_question.difficulty))

        retrieved_context = ""
        if self.document_rag is not None:
            chunks = self.document_rag.retrieve_context(
                user_id=user_id,
                query=f"{parent_question.topic} {parent_question.question_text}",
                subject=session["subject"],
                match_count=6,
            )
            retrieved_context = format_retrieved_context(chunks)

        self.web_rag.gemini = self.gemini
        web_result = self.web_rag.retrieve_context(
            f"Academic subject: {session['subject']}. Topic: {parent_question.topic}. "
            f"Original question: {parent_question.question_text}. "
            "Find current or externally verifiable context only if it can help formulate a precise Socratic follow-up. "
            "Prefer authoritative sources."
        )
        if web_result.context:
            retrieved_context = (
                f"{retrieved_context}\n\n" if retrieved_context else ""
            ) + "Grounded web context:\n" + web_result.context

        prompt = build_followup_prompt(
            subject=session["subject"],
            topic=parent_question.topic,
            exam_mode=session["exam_mode"],
            difficulty=difficulty,
            original_question=parent_question.question_text,
            student_answer=answer_text,
            missing_concepts=evaluation.missing_concepts,
            misconceptions=evaluation.misconceptions,
            followup_number=number,
            retrieved_context=retrieved_context,
        )

        result = self.gemini.generate_structured(prompt, QuestionGenerationResult)
        validate_generated_question(result, [parent_question.topic])

        if result.question_type != QuestionType.FOLLOW_UP:
            raise ValueError("Generated follow-up must use the follow_up question type.")

        row = self.questions.create_and_ask({
            "exam_session_id": str(session_id),
            "parent_question_id": str(parent_question.id),
            "topic": parent_question.topic,
            "difficulty": difficulty,
            "question_type": QuestionType.FOLLOW_UP.value,
            "question_text": result.question_text.strip(),
            "expected_points": [x.strip() for x in result.expected_points if x.strip()][:5],
            "status": QuestionStatus.GENERATED.value,
            "sequence_number": self.questions.get_latest_sequence(session_id) + 1,
            "is_follow_up": True,
        })

        qid = row["id"] if isinstance(row["id"], UUID) else UUID(str(row["id"]))
        self.exams.set_current_question(session_id, user_id, qid)
        return QuestionRecord.model_validate(self.questions.get_for_session(qid, session_id))
