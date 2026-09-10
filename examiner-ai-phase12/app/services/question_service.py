
from __future__ import annotations

from uuid import UUID

from app.ai.gemini_client import GeminiClient
from app.ai.prompts.question import (
    build_question_generation_prompt,
    validate_generated_question,
)
from app.db.repositories.factory import get_repositories
from app.models.enums import QuestionStatus
from app.schemas.ai import QuestionGenerationResult
from app.schemas.domain import QuestionRecord
from app.services.adaptive_service import AdaptiveEngine
from app.rag.document_rag import DocumentRAGService
from app.rag.context import format_retrieved_context
from app.rag.web_rag import WebRAGService


class QuestionService:
    """Orchestrates deterministic question selection and Gemini generation."""

    def __init__(self, repositories: dict | None = None, gemini: GeminiClient | None = None):
        self.repositories = repositories or get_repositories()
        self.exams = self.repositories["exams"]
        self.questions = self.repositories["questions"]
        self.gemini = gemini or GeminiClient()
        self.adaptive = AdaptiveEngine(self.repositories)
        self.document_rag = DocumentRAGService(self.repositories) if "documents" in self.repositories else None
        self.web_rag = WebRAGService(self.gemini)

    def generate_next_main_question(
        self, user_id: UUID, session_id: UUID
    ) -> QuestionRecord:
        session_row = self.exams.get_for_user(session_id, user_id)
        if not session_row:
            raise LookupError("Exam session not found.")
        if session_row["status"] != "in_progress":
            raise ValueError("Questions can only be generated for an in-progress exam.")

        # Never create a second current question. The answer/evaluation phase
        # will release the current question later.
        current = self.questions.get_current(session_id)
        if current:
            return QuestionRecord.model_validate(current)

        main_count = self.exams.count_questions(session_id)
        if main_count >= int(session_row["question_count"]):
            raise ValueError("The configured question limit has been reached.")

        previous = self.questions.list_for_session(session_id)
        allowed_topics = list(session_row["topics"])

        decision = self.adaptive.select_next(user_id, session_id)
        target_topic = decision.target_topic
        difficulty = decision.difficulty

        retrieved_context = ""
        if self.document_rag is not None:
            context_chunks = self.document_rag.retrieve_context(
                user_id=user_id,
                query=f"{session_row['subject']} {target_topic}",
                subject=session_row["subject"],
                match_count=6,
            )
            retrieved_context = format_retrieved_context(context_chunks)

        self.web_rag.gemini = self.gemini
        web_result = self.web_rag.retrieve_context(
            f"Academic subject: {session_row['subject']}. Topic: {target_topic}. "
            "Find current or externally verifiable information that could improve an examination question. "
            "Prefer authoritative technical or academic sources."
        )
        if web_result.context:
            retrieved_context = (
                f"{retrieved_context}\n\n" if retrieved_context else ""
            ) + "Grounded web context:\n" + web_result.context

        prompt = build_question_generation_prompt(
            subject=session_row["subject"],
            topics=allowed_topics,
            exam_mode=session_row["exam_mode"],
            target_topic=target_topic,
            difficulty=difficulty,
            question_number=main_count + 1,
            previous_questions=[row["question_text"] for row in previous],
            retrieved_context=retrieved_context,
        )

        result = self.gemini.generate_structured(prompt, QuestionGenerationResult)
        validate_generated_question(result, allowed_topics)

        row = self.questions.create_and_ask(
            {
                "exam_session_id": str(session_id),
                "parent_question_id": None,
                "topic": result.topic,
                "difficulty": result.difficulty,
                "question_type": result.question_type.value,
                "question_text": result.question_text.strip(),
                "expected_points": [p.strip() for p in result.expected_points if p.strip()],
                "status": QuestionStatus.GENERATED.value,
                "sequence_number": self.questions.get_latest_sequence(session_id) + 1,
                "is_follow_up": False,
            }
        )
        question_id = row["id"] if isinstance(row["id"], UUID) else UUID(row["id"])
        self.exams.set_current_question(session_id, user_id, question_id)
        stored = self.questions.get_for_session(question_id, session_id)
        return QuestionRecord.model_validate(stored)
