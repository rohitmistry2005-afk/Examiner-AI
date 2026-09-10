from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from app.schemas.ai import AdaptiveDecisionResult

from app.models.enums import (
    DocumentSourceType,
    EvaluationDecision,
    ExamMode,
    ExamSessionStatus,
    QuestionStatus,
    QuestionType,
)


class DBModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ExamSessionRecord(DBModel):
    id: UUID
    user_id: UUID
    subject: str
    topics: list[str]
    exam_mode: ExamMode
    initial_difficulty: int = Field(ge=1, le=5)
    question_count: int = Field(ge=1, le=100)
    status: ExamSessionStatus
    current_question_id: UUID | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class QuestionRecord(DBModel):
    id: UUID
    exam_session_id: UUID
    parent_question_id: UUID | None = None
    topic: str
    difficulty: int = Field(ge=1, le=5)
    question_type: QuestionType
    question_text: str
    expected_points: list[str]
    status: QuestionStatus
    sequence_number: int = Field(ge=1)
    is_follow_up: bool
    created_at: datetime
    answered_at: datetime | None = None


class AnswerRecord(DBModel):
    id: UUID
    question_id: UUID
    exam_session_id: UUID
    user_id: UUID
    answer_text: str
    submitted_at: datetime


class EvaluationRecord(DBModel):
    id: UUID
    answer_id: UUID
    question_id: UUID
    score: float = Field(ge=0, le=10)
    correctness: float = Field(ge=0, le=1)
    completeness: float = Field(ge=0, le=1)
    conceptual_understanding: float = Field(ge=0, le=1)
    strengths: list[str]
    missing_concepts: list[str]
    misconceptions: list[str]
    feedback: str
    decision: EvaluationDecision
    created_at: datetime


class KnowledgeStateRecord(DBModel):
    id: UUID
    user_id: UUID
    exam_session_id: UUID
    topic: str
    mastery_score: float = Field(ge=0, le=1)
    current_difficulty: int = Field(ge=1, le=5)
    strong_concepts: list[str]
    weak_concepts: list[str]
    misconceptions: list[str]
    attempts: int = Field(ge=0)
    updated_at: datetime


class TopicPerformanceRecord(DBModel):
    id: UUID
    user_id: UUID
    exam_session_id: UUID
    topic: str
    questions_attempted: int = Field(ge=0)
    average_score: float = Field(ge=0, le=10)
    accuracy: float = Field(ge=0, le=1)
    updated_at: datetime


class DocumentRecord(DBModel):
    id: UUID
    user_id: UUID
    subject: str | None = None
    filename: str
    mime_type: str
    source_type: DocumentSourceType
    storage_path: str | None = None
    status: str
    created_at: datetime


class DocumentChunkRecord(DBModel):
    id: UUID
    document_id: UUID
    user_id: UUID
    content: str
    page_number: int | None = None
    chunk_index: int = Field(ge=0)
    embedding: list[float]
    created_at: datetime


class PerformanceSummary(BaseModel):
    exam_session_id: UUID
    overall_score: float = Field(ge=0, le=10)
    configured_main_questions: int = Field(ge=0)
    generated_main_questions: int = Field(ge=0)
    answered_main_questions: int = Field(ge=0)
    follow_up_questions: int = Field(ge=0)
    evaluated_answers: int = Field(ge=0)
    evaluated_follow_up_answers: int = Field(ge=0)
    topic_coverage: float = Field(ge=0, le=1)
    average_correctness: float = Field(ge=0, le=1)
    average_completeness: float = Field(ge=0, le=1)
    average_conceptual_understanding: float = Field(ge=0, le=1)
    strong_topics: list[str]
    weak_topics: list[str]
    concepts_to_revise: list[str]
    misconceptions: list[str]
    topic_breakdown: list[dict]


class ReportRecord(DBModel):
    id: UUID
    exam_session_id: UUID
    user_id: UUID
    overall_score: float = Field(ge=0, le=10)
    summary: str
    strong_areas: list[str]
    weak_areas: list[str]
    concepts_to_revise: list[str]
    recommendations: list[str]
    closing_feedback: str
    performance_snapshot: dict
    created_at: datetime


class ExamCreateRequest(BaseModel):
    subject: str = Field(min_length=1, max_length=200)
    topics: list[str] = Field(min_length=1, max_length=50)
    exam_mode: ExamMode
    difficulty: int = Field(ge=1, le=5)
    question_count: int = Field(ge=1, le=100)

    def normalized(self) -> "ExamCreateRequest":
        subject = " ".join(self.subject.split())
        seen: set[str] = set()
        topics: list[str] = []
        for raw in self.topics:
            topic = " ".join(raw.split())
            key = topic.casefold()
            if topic and key not in seen:
                seen.add(key)
                topics.append(topic)
        if not topics:
            raise ValueError("At least one non-empty topic is required.")
        return self.model_copy(update={"subject": subject, "topics": topics})


class ExamStartResponse(BaseModel):
    session: ExamSessionRecord
    question: QuestionRecord | None = None


class ExamCompletionResponse(BaseModel):
    session: ExamSessionRecord


class CurrentQuestionResponse(BaseModel):
    question: QuestionRecord | None
    exam_completed: bool = False


class AnswerSubmissionRequest(BaseModel):
    answer_text: str = Field(min_length=1, max_length=20000)

    def normalized(self) -> "AnswerSubmissionRequest":
        answer = " ".join(self.answer_text.split())
        if not answer:
            raise ValueError("Answer cannot be empty.")
        return self.model_copy(update={"answer_text": answer})


class AnswerSubmissionResponse(BaseModel):
    answer: AnswerRecord
    evaluation: EvaluationRecord

class ChatTurnRequest(BaseModel):
    question_id: UUID
    answer_text: str = Field(min_length=1, max_length=20000)

    def normalized(self) -> "ChatTurnRequest":
        answer = " ".join(self.answer_text.split())
        if not answer:
            raise ValueError("Answer cannot be empty.")
        return self.model_copy(update={"answer_text": answer})


class ChatTurnResponse(BaseModel):
    examiner_message: str = Field(min_length=1, max_length=10000)
    answer: AnswerRecord
    evaluation: EvaluationRecord
    adaptive_decision: AdaptiveDecisionResult
    next_question: QuestionRecord | None = None
    exam_completed: bool = False
