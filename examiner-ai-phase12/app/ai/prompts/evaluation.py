from __future__ import annotations


def build_answer_evaluation_prompt(
    *,
    subject: str,
    topic: str,
    exam_mode: str,
    difficulty: int,
    question_text: str,
    expected_points: list[str],
    answer_text: str,
    retrieved_context: str | None = None,
) -> str:
    points = "\n".join(f"- {point}" for point in expected_points)
    return f"""
You are ExaminerAI's semantic answer evaluator.

Evaluate the student's answer against the question and expected answer points.
Judge meaning and demonstrated understanding, not keyword overlap.
Do not invent claims that are not supported by the student's response.
Score the answer on a 0-10 scale.

Subject: {subject}
Topic: {topic}
Exam mode: {exam_mode}
Question difficulty: {difficulty}

Question:
{question_text}

Expected answer points:
{points}

Student answer:
{answer_text}

Return JSON matching the provided evaluation schema with:
- score: 0 to 10
- correctness: 0 to 1
- completeness: 0 to 1
- conceptual_understanding: 0 to 1
- strengths: concise evidence-based strengths
- missing_concepts: concepts required by the question but missing
- misconceptions: specific incorrect or confused concepts, if any
- feedback: concise, useful examiner feedback
""".strip()
