from __future__ import annotations

from uuid import UUID

from app.ai.gemini_client import GeminiClient
from app.ai.prompts.evaluation import build_answer_evaluation_prompt
from app.db.repositories.factory import get_repositories
from app.models.enums import EvaluationDecision, ExamSessionStatus, QuestionStatus
from app.schemas.ai import AnswerEvaluationResult
from app.schemas.domain import AnswerRecord, EvaluationRecord, QuestionRecord
from app.services.knowledge_service import KnowledgeStateService
from app.rag.document_rag import DocumentRAGService
from app.rag.context import format_retrieved_context
from app.rag.web_rag import WebRAGService


class EvaluationService:
    """Persist a free-form answer and produce one validated AI evaluation."""

    def __init__(self, repositories: dict | None = None, gemini: GeminiClient | None = None):
        self.repositories = repositories or get_repositories()
        self.exams = self.repositories["exams"]
        self.questions = self.repositories["questions"]
        self.answers = self.repositories["answers"]
        self.evaluations = self.repositories["evaluations"]
        self.knowledge_service = KnowledgeStateService(self.repositories) if "knowledge" in self.repositories and "performance" in self.repositories else None
        self.gemini = gemini or GeminiClient()
        self.document_rag = DocumentRAGService(self.repositories) if "documents" in self.repositories else None
        self.web_rag = WebRAGService(self.gemini)

    def submit_answer(
        self, user_id: UUID, session_id: UUID, question_id: UUID, answer_text: str
    ) -> tuple[AnswerRecord, EvaluationRecord]:
        session_row = self.exams.get_for_user(session_id, user_id)
        if not session_row:
            raise LookupError("Exam session not found.")
        if session_row["status"] != ExamSessionStatus.IN_PROGRESS.value:
            raise ValueError("Answers can only be submitted for an in-progress exam.")

        question_row = self.questions.get_for_session(question_id, session_id)
        if not question_row:
            raise LookupError("Question not found.")

        if question_row.get("status") == QuestionStatus.ANSWERED.value:
            raise ValueError("This question has already been answered.")
        current_id = session_row.get("current_question_id")
        if current_id and str(current_id) != str(question_id):
            raise ValueError("Only the current question can be answered.")

        existing_answer = self.answers.get_for_question_and_user(question_id, user_id)
        if existing_answer:
            existing_answer_id = existing_answer["id"] if isinstance(existing_answer["id"], UUID) else UUID(str(existing_answer["id"]))
            existing_evaluation = self.evaluations.get_for_answer(existing_answer_id)
            if existing_evaluation:
                return (
                    AnswerRecord.model_validate(existing_answer),
                    EvaluationRecord.model_validate(existing_evaluation),
                )
            raise ValueError("An answer already exists but has no evaluation.")

        question = QuestionRecord.model_validate(question_row)
        normalized = " ".join(answer_text.split())
        if not normalized:
            raise ValueError("Answer cannot be empty.")

        answer_row = self.answers.create(
            {
                "question_id": str(question_id),
                "exam_session_id": str(session_id),
                "user_id": str(user_id),
                "answer_text": normalized,
            }
        )

        retrieved_context = ""
        if self.document_rag is not None:
            chunks = self.document_rag.retrieve_context(
                user_id=user_id,
                query=f"{question.topic} {question.question_text}",
                subject=session_row["subject"],
                match_count=6,
            )
            retrieved_context = format_retrieved_context(chunks)

        self.web_rag.gemini = self.gemini
        web_result = self.web_rag.retrieve_context(
            f"Academic subject: {session_row['subject']}. Topic: {question.topic}. "
            f"Question: {question.question_text}. Assess whether current or externally verifiable context is relevant "
            "to evaluating the student's answer. Prefer authoritative sources."
        )
        if web_result.context:
            retrieved_context = (
                f"{retrieved_context}\n\n" if retrieved_context else ""
            ) + "Grounded web context:\n" + web_result.context

        prompt = build_answer_evaluation_prompt(
            subject=session_row["subject"],
            topic=question.topic,
            exam_mode=session_row["exam_mode"],
            difficulty=question.difficulty,
            question_text=question.question_text,
            expected_points=question.expected_points,
            answer_text=normalized,
            retrieved_context=retrieved_context,
        )
        result = self.gemini.generate_structured(prompt, AnswerEvaluationResult)

        evaluation_row = self.evaluations.create(
            {
                "answer_id": str(answer_row["id"]),
                "question_id": str(question_id),
                "score": result.score,
                "correctness": result.correctness,
                "completeness": result.completeness,
                "conceptual_understanding": result.conceptual_understanding,
                "strengths": result.strengths,
                "missing_concepts": result.missing_concepts,
                "misconceptions": result.misconceptions,
                "feedback": result.feedback,
                # Adaptive/follow-up policy is Phase 7/8; Phase 5 only evaluates.
                "decision": EvaluationDecision.NEXT.value,
            }
        )

        self.questions.mark_answered(question_id, session_id)
        self.exams.clear_current_question(session_id, user_id)

        evaluation = EvaluationRecord.model_validate(evaluation_row)

        # Phase 6: persist topic-level knowledge evidence and performance.
        # Phase 7 will consume this state for adaptive next-question decisions.
        if self.knowledge_service is not None:
            self.knowledge_service.process_evaluation(
                user_id=user_id,
                session_id=session_id,
                topic=question.topic,
                evaluation=evaluation,
                question_difficulty=question.difficulty,
            )

        return (
            AnswerRecord.model_validate(answer_row),
            evaluation,
        )
