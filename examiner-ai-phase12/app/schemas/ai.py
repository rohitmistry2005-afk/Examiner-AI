
from pydantic import BaseModel, Field

from app.models.enums import QuestionType


class QuestionGenerationResult(BaseModel):
    question_text: str = Field(min_length=10, max_length=5000)
    topic: str = Field(min_length=1, max_length=200)
    difficulty: int = Field(ge=1, le=5)
    question_type: QuestionType
    expected_points: list[str] = Field(min_length=3, max_length=7)


class AnswerEvaluationResult(BaseModel):
    score: float = Field(ge=0, le=10)
    correctness: float = Field(ge=0, le=1)
    completeness: float = Field(ge=0, le=1)
    conceptual_understanding: float = Field(ge=0, le=1)
    strengths: list[str] = Field(max_length=7)
    missing_concepts: list[str] = Field(max_length=10)
    misconceptions: list[str] = Field(max_length=10)
    feedback: str = Field(min_length=1, max_length=5000)

class AdaptiveDecisionResult(BaseModel):
    action: str = Field(
        pattern=r"^(advance|reinforce|increase_difficulty|decrease_difficulty|maintain)$"
    )
    target_topic: str = Field(min_length=1, max_length=200)
    difficulty: int = Field(ge=1, le=5)
    reason: str = Field(min_length=1, max_length=1000)


class FinalReportContent(BaseModel):
    summary: str = Field(min_length=1, max_length=5000)
    strong_areas: list[str] = Field(max_length=10)
    weak_areas: list[str] = Field(max_length=10)
    concepts_to_revise: list[str] = Field(max_length=20)
    recommendations: list[str] = Field(max_length=10)
    closing_feedback: str = Field(min_length=1, max_length=5000)
