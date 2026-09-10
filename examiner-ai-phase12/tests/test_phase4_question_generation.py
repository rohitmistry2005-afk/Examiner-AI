
from uuid import UUID, uuid4

from app.models.enums import QuestionType
from app.schemas.ai import QuestionGenerationResult
from app.services.question_service import QuestionService


class FakeExams:
    def __init__(self):
        self.rows = {}
        self.question_counts = {}
        self.current_question_ids = {}

    def get_for_user(self, session_id, user_id):
        row = self.rows.get(session_id)
        return row if row and row["user_id"] == str(user_id) else None

    def count_questions(self, session_id):
        return self.question_counts.get(session_id, 0)

    def set_current_question(self, session_id, user_id, question_id):
        self.current_question_ids[session_id] = question_id
        self.rows[session_id]["current_question_id"] = str(question_id)
        return self.rows[session_id]


class FakeQuestions:
    def __init__(self, exams):
        self.exams = exams
        self.rows = []

    def get_current(self, session_id):
        for row in reversed(self.rows):
            if row["exam_session_id"] == str(session_id) and row["status"] == "asked":
                return row
        return None

    def list_for_session(self, session_id):
        return [r for r in self.rows if r["exam_session_id"] == str(session_id)]

    def get_latest_sequence(self, session_id):
        rows = self.list_for_session(session_id)
        return max([r["sequence_number"] for r in rows], default=0)

    def create_and_ask(self, payload):
        row = {
            "id": uuid4(),
            **payload,
            "status": "asked",
            "created_at": "2026-09-10T11:01:00Z",
            "answered_at": None,
        }
        self.rows.append(row)
        self.exams.question_counts[UUID(payload["exam_session_id"])] += 1
        return row

    def get_for_session(self, question_id, session_id):
        for row in self.rows:
            if row["id"] == question_id and row["exam_session_id"] == str(session_id):
                return row
        raise LookupError("Question not found.")


class FakeGemini:
    def __init__(self, result):
        self.result = result
        self.prompts = []

    def generate_structured(self, prompt, schema):
        self.prompts.append(prompt)
        assert schema is QuestionGenerationResult
        return self.result


def setup():
    user_id = uuid4()
    session_id = uuid4()
    exams = FakeExams()
    exams.rows[session_id] = {
        "id": session_id,
        "user_id": str(user_id),
        "subject": "DBMS",
        "topics": ["SQL", "Normalization"],
        "exam_mode": "semester",
        "initial_difficulty": 3,
        "question_count": 3,
        "status": "in_progress",
        "current_question_id": None,
    }
    exams.question_counts[session_id] = 0
    questions = FakeQuestions(exams)
    result = QuestionGenerationResult(
        question_text="Explain third normal form.",
        topic="Normalization",
        difficulty=3,
        question_type=QuestionType.CONCEPTUAL,
        expected_points=[
            "2NF prerequisite",
            "Transitive dependency",
            "Non-prime attributes",
        ],
    )
    gemini = FakeGemini(result)
    service = QuestionService(
        repositories={"exams": exams, "questions": questions},
        gemini=gemini,
    )
    return service, exams, questions, gemini, user_id, session_id


def test_generates_and_persists_first_question():
    service, exams, questions, gemini, user_id, session_id = setup()
    record = service.generate_next_main_question(user_id, session_id)

    assert record.topic == "Normalization"
    assert record.status.value == "asked"
    assert record.sequence_number == 1
    assert len(gemini.prompts) == 1
    assert exams.rows[session_id]["current_question_id"] == str(record.id)


def test_existing_current_question_is_reused_without_second_gemini_call():
    service, exams, questions, gemini, user_id, session_id = setup()
    first = service.generate_next_main_question(user_id, session_id)
    second = service.generate_next_main_question(user_id, session_id)

    assert first.id == second.id
    assert len(gemini.prompts) == 1


def test_generated_topic_must_be_in_configured_topics():
    service, _, _, _, user_id, session_id = setup()
    service.gemini = FakeGemini(
        QuestionGenerationResult(
            question_text="Explain a concept.",
            topic="Operating Systems",
            difficulty=3,
            question_type=QuestionType.CONCEPTUAL,
            expected_points=["A", "B", "C"],
        )
    )

    import pytest

    with pytest.raises(ValueError, match="outside the configured topics"):
        service.generate_next_main_question(user_id, session_id)


def test_generation_respects_main_question_limit():
    service, exams, questions, gemini, user_id, session_id = setup()
    exams.rows[session_id]["question_count"] = 1
    first = service.generate_next_main_question(user_id, session_id)
    assert first.sequence_number == 1
    assert len(gemini.prompts) == 1
