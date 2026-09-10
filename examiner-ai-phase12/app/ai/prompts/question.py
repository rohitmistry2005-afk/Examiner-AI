
from app.models.enums import ExamMode
from app.schemas.ai import QuestionGenerationResult


def build_question_generation_prompt(
    *,
    subject: str,
    topics: list[str],
    exam_mode: ExamMode | str,
    target_topic: str,
    difficulty: int,
    question_number: int,
    previous_questions: list[str] | None = None,
    retrieved_context: str | None = None,
) -> str:
    previous = previous_questions or []
    prior_block = "\n".join(f"- {q}" for q in previous[-10:]) or "- None"

    return f"""
You are ExaminerAI, an expert technical examiner.

Generate exactly ONE examination question.

Exam context:
- Subject: {subject}
- Allowed syllabus topics: {", ".join(topics)}
- Exam mode: {exam_mode.value if isinstance(exam_mode, ExamMode) else exam_mode}
- Target topic for this question: {target_topic}
- Difficulty: {difficulty}/5
- Main question number: {question_number}

Requirements:
1. Stay strictly within the supplied subject and topic list.
2. Test understanding, not trivia or wording memorization.
3. Match the requested difficulty and exam mode.
4. Generate a self-contained question that a college student can answer without
   missing context.
5. Provide 3-7 concise expected answer points that an evaluator can use later.
6. Do not include the answer in question_text.
7. Do not repeat or trivially paraphrase a recent question.

Recent questions:
{prior_block}

Grounded document context:
{retrieved_context or "- No user document context available."}
""".strip()


def validate_generated_question(result: QuestionGenerationResult, allowed_topics: list[str]) -> None:
    allowed = {topic.casefold() for topic in allowed_topics}
    if result.topic.casefold() not in allowed:
        raise ValueError("Gemini generated a question outside the configured topics.")
    if not result.question_text.strip():
        raise ValueError("Generated question text is empty.")
    if not 1 <= result.difficulty <= 5:
        raise ValueError("Generated question difficulty is outside the allowed range.")
    if not 3 <= len(result.expected_points) <= 7:
        raise ValueError("Generated question must contain 3-7 expected answer points.")
