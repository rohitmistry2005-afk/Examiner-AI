from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.models.enums import ExamMode, ExamSessionStatus, QuestionType
from app.schemas.domain import ExamSessionRecord, QuestionRecord


def test_domain_enum_values_are_stable():
    assert ExamMode.VIVA.value == "viva"
    assert ExamSessionStatus.IN_PROGRESS.value == "in_progress"
    assert QuestionType.FOLLOW_UP.value == "follow_up"


def test_exam_session_schema_validates_difficulty_and_count():
    record = ExamSessionRecord(
        id=uuid4(), user_id=uuid4(), subject="DBMS", topics=["SQL"],
        exam_mode=ExamMode.SEMESTER, initial_difficulty=3, question_count=10,
        status=ExamSessionStatus.CREATED, created_at="2026-09-10T10:00:00Z",
        updated_at="2026-09-10T10:00:00Z",
    )
    assert record.question_count == 10

    with pytest.raises(ValidationError):
        ExamSessionRecord(
            id=uuid4(), user_id=uuid4(), subject="DBMS", topics=["SQL"],
            exam_mode=ExamMode.SEMESTER, initial_difficulty=7, question_count=10,
            status=ExamSessionStatus.CREATED, created_at="2026-09-10T10:00:00Z",
            updated_at="2026-09-10T10:00:00Z",
        )


def test_question_schema_supports_follow_up_parent():
    parent = uuid4()
    record = QuestionRecord(
        id=uuid4(), exam_session_id=uuid4(), parent_question_id=parent,
        topic="Normalization", difficulty=2, question_type=QuestionType.FOLLOW_UP,
        question_text="Why is this not 3NF?", expected_points=["transitive dependency"],
        status="generated", sequence_number=2, is_follow_up=True,
        created_at="2026-09-10T10:00:00Z",
    )
    assert record.parent_question_id == parent
    assert record.is_follow_up is True
