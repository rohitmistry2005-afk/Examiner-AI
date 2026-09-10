from __future__ import annotations

from app.models.enums import ExamMode


def build_followup_prompt(
    *,
    subject: str,
    topic: str,
    exam_mode: ExamMode | str,
    difficulty: int,
    original_question: str,
    student_answer: str,
    missing_concepts: list[str],
    misconceptions: list[str],
    followup_number: int,
    retrieved_context: str | None = None,
) -> str:
    missing = "\n".join(f"- {x}" for x in missing_concepts[:5]) or "- None"
    errors = "\n".join(f"- {x}" for x in misconceptions[:5]) or "- None"
    mode = exam_mode.value if isinstance(exam_mode, ExamMode) else exam_mode

    return f'''
You are ExaminerAI, an expert technical examiner conducting a conversational examination.

Generate exactly ONE targeted Socratic follow-up question.

The student has just answered an original question. The follow-up must probe the
specific missing concept or misconception rather than teaching the answer.

Context:
- Subject: {subject}
- Topic: {topic}
- Exam mode: {mode}
- Difficulty: {difficulty}/5
- Follow-up number: {followup_number}

Original question:
{original_question}

Student answer:
{student_answer}

Missing concepts:
{missing}

Misconceptions:
{errors}

Relevant user-provided document context:
{retrieved_context or "- No user document context available."}

Rules:
1. Stay within the original topic and question.
2. Ask exactly one concise question.
3. Do not reveal the answer.
4. Naturally sound like an examiner speaking to a student.
5. Provide 3-5 expected answer points for later semantic evaluation.
6. Set question_type to "follow_up".
'''.strip()
