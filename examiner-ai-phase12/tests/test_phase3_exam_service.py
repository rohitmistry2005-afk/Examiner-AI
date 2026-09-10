from uuid import uuid4

import pytest

from app.models.enums import ExamMode, ExamSessionStatus
from app.schemas.domain import ExamCreateRequest
from app.services.exam_service import ExamService


class FakeExams:
    def __init__(self):
        self.rows = {}
        self.created = 0

    def create(self, payload):
        self.created += 1
        row = {
            "id": uuid4(),
            "user_id": uuid4(),
            "subject": payload["subject"],
            "topics": payload["topics"],
            "exam_mode": payload["exam_mode"],
            "initial_difficulty": payload["initial_difficulty"],
            "question_count": payload["question_count"],
            "status": payload["status"],
            "current_question_id": None,
            "started_at": None,
            "completed_at": None,
            "created_at": "2026-09-10T10:00:00Z",
            "updated_at": "2026-09-10T10:00:00Z",
        }
        row["user_id"] = payload["user_id"]
        self.rows[row["id"]] = row
        return row

    def get_for_user(self, session_id, user_id):
        return self.rows.get(session_id)

    def list_for_user(self, user_id):
        return [r for r in self.rows.values() if r["user_id"] == str(user_id)]

    def update_for_user(self, session_id, user_id, payload):
        row = self.rows[session_id]
        row.update(payload)
        row["updated_at"] = "2026-09-10T11:00:00Z"
        return row

    def start(self, session_id, user_id):
        return self.update_for_user(session_id, user_id, {
            "status": "in_progress",
            "started_at": "2026-09-10T11:00:00Z",
        })

    def complete(self, session_id, user_id):
        return self.update_for_user(session_id, user_id, {
            "status": "completed",
            "completed_at": "2026-09-10T11:30:00Z",
            "current_question_id": None,
        })

    def count_questions(self, session_id):
        return 0


class FakeQuestions:
    def get_current(self, session_id):
        return None


def make_service():
    repo = FakeExams()
    service = ExamService({"exams": repo, "questions": FakeQuestions()})
    return service, repo


def test_create_normalizes_and_deduplicates_topics():
    service, repo = make_service()
    request = ExamCreateRequest(
        subject="  DBMS  ",
        topics=[" SQL ", "sql", "Normalization"],
        exam_mode=ExamMode.SEMESTER,
        difficulty=3,
        question_count=10,
    )
    record = service.create_exam(uuid4(), request)
    assert record.subject == "DBMS"
    assert record.topics == ["SQL", "Normalization"]
    assert repo.created == 1


def test_start_then_complete():
    service, repo = make_service()
    user_id = uuid4()
    record = service.create_exam(
        user_id,
        ExamCreateRequest(
            subject="DBMS",
            topics=["SQL"],
            exam_mode=ExamMode.SEMESTER,
            difficulty=3,
            question_count=5,
        ),
    )

    started = service.start_exam(user_id, record.id).session
    assert started.status == ExamSessionStatus.IN_PROGRESS

    completed = service.complete_exam(user_id, record.id).session
    assert completed.status == ExamSessionStatus.COMPLETED


def test_cannot_complete_created_exam():
    service, _ = make_service()
    user_id = uuid4()
    record = service.create_exam(
        user_id,
        ExamCreateRequest(
            subject="DBMS",
            topics=["SQL"],
            exam_mode=ExamMode.SEMESTER,
            difficulty=3,
            question_count=5,
        ),
    )
    with pytest.raises(ValueError, match="must be started"):
        service.complete_exam(user_id, record.id)


def test_created_exam_has_no_current_question_yet():
    service, _ = make_service()
    user_id = uuid4()
    record = service.create_exam(
        user_id,
        ExamCreateRequest(
            subject="DBMS",
            topics=["SQL"],
            exam_mode=ExamMode.SEMESTER,
            difficulty=3,
            question_count=5,
        ),
    )
    service.start_exam(user_id, record.id)
    current = service.get_current_question(user_id, record.id)
    assert current.question is None
    assert current.exam_completed is False
