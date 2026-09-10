from uuid import uuid4

from app.models.enums import EvaluationDecision, QuestionStatus, QuestionType
from app.schemas.ai import QuestionGenerationResult
from app.schemas.domain import EvaluationRecord, QuestionRecord
from app.services.followup_service import FollowUpService


class FakeExams:
    def __init__(self, sid, uid):
        self.row = {
            "id": str(sid), "user_id": str(uid), "subject": "DBMS",
            "topics": ["Normalization"], "exam_mode": "viva",
            "status": "in_progress", "current_question_id": None,
        }

    def get_for_user(self, sid, uid):
        return self.row

    def set_current_question(self, sid, uid, qid):
        self.row["current_question_id"] = str(qid)


class FakeQuestions:
    def __init__(self):
        self.rows = []

    def list_for_session(self, sid):
        return self.rows

    def get_latest_sequence(self, sid):
        return max([r["sequence_number"] for r in self.rows] or [0])

    def create_and_ask(self, payload):
        row = {
            "id": str(uuid4()),
            "created_at": "2026-09-10T12:02:00Z",
            "answered_at": None,
            **payload,
        }
        self.rows.append(row)
        return row

    def get_for_session(self, qid, sid):
        return next((r for r in self.rows if str(r["id"]) == str(qid)), None)


class FakeGemini:
    def __init__(self, result):
        self.result = result
        self.calls = 0

    def generate_structured(self, prompt, schema):
        self.calls += 1
        return self.result


def make_eval(
    score=4,
    correctness=.4,
    completeness=.4,
    conceptual=.4,
    missing=None,
    misconceptions=None,
):
    return EvaluationRecord(
        id=uuid4(), answer_id=uuid4(), question_id=uuid4(),
        score=score, correctness=correctness,
        completeness=completeness, conceptual_understanding=conceptual,
        strengths=[],
        missing_concepts=missing if missing is not None else ["transitive dependency"],
        misconceptions=misconceptions or [],
        feedback="Needs more detail.",
        decision=EvaluationDecision.NEXT,
        created_at="2026-09-10T12:00:00Z",
    )


def parent(sid):
    return QuestionRecord(
        id=uuid4(), exam_session_id=sid, parent_question_id=None,
        topic="Normalization", difficulty=3,
        question_type=QuestionType.CONCEPTUAL,
        question_text="Explain 3NF.", expected_points=["A", "B", "C"],
        status=QuestionStatus.ANSWERED, sequence_number=1,
        is_follow_up=False, created_at="2026-09-10T12:00:00Z",
        answered_at="2026-09-10T12:01:00Z"
    )


def setup():
    uid, sid = uuid4(), uuid4()
    exams = FakeExams(sid, uid)
    questions = FakeQuestions()
    gemini = FakeGemini(QuestionGenerationResult(
        question_text="What dependency does 3NF remove?",
        topic="Normalization", difficulty=3,
        question_type=QuestionType.FOLLOW_UP,
        expected_points=["transitive dependency", "non-key attribute", "dependency"],
    ))
    service = FollowUpService(
        repositories={"exams": exams, "questions": questions},
        gemini=gemini,
    )
    return service, uid, sid, gemini, questions


def test_incomplete_answer_generates_child_followup():
    service, uid, sid, gemini, questions = setup()
    result = service.create_follow_up(
        uid, sid, parent(sid), "answer", make_eval()
    )
    assert result is not None
    assert result.is_follow_up is True
    assert result.parent_question_id is not None
    assert result.question_type == QuestionType.FOLLOW_UP
    assert gemini.calls == 1
    assert len(questions.rows) == 1


def test_strong_answer_does_not_trigger_followup():
    service, uid, sid, gemini, questions = setup()
    strong = make_eval(
        score=9, correctness=.95, completeness=.95,
        conceptual=.95, missing=[], misconceptions=[]
    )
    assert service.create_follow_up(
        uid, sid, parent(sid), "strong answer", strong
    ) is None
    assert gemini.calls == 0


def test_maximum_two_followups():
    service, uid, sid, gemini, questions = setup()
    p = parent(sid)
    questions.rows.extend([
        {
            "id": str(uuid4()),
            "parent_question_id": str(p.id),
            "is_follow_up": True,
            "sequence_number": 2,
            "exam_session_id": str(sid),
        },
        {
            "id": str(uuid4()),
            "parent_question_id": str(p.id),
            "is_follow_up": True,
            "sequence_number": 3,
            "exam_session_id": str(sid),
        },
    ])
    assert service.create_follow_up(uid, sid, p, "answer", make_eval()) is None
    assert gemini.calls == 0


def test_followup_cannot_escape_parent_topic():
    service, uid, sid, gemini, questions = setup()
    service.gemini = FakeGemini(QuestionGenerationResult(
        question_text="What is a process?",
        topic="Operating Systems", difficulty=3,
        question_type=QuestionType.FOLLOW_UP,
        expected_points=["A", "B", "C"],
    ))
    try:
        service.create_follow_up(uid, sid, parent(sid), "answer", make_eval())
    except ValueError as exc:
        assert "outside the configured topics" in str(exc)
    else:
        raise AssertionError("Expected topic validation to reject follow-up")
