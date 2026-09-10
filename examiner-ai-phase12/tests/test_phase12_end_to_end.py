
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.ai.gemini_client import GroundedTextResult
from app.api.exams import (
    get_conversation_service,
    get_evaluation_service,
    get_exam_service,
    get_knowledge_service,
    get_report_service,
)
from app.core.security import get_current_user_id
from app.main import app
from app.schemas.ai import AnswerEvaluationResult, FinalReportContent, QuestionGenerationResult
from app.services.conversation_service import ConversationService
from app.services.evaluation_service import EvaluationService
from app.services.exam_service import ExamService
from app.services.knowledge_service import KnowledgeStateService
from app.services.question_service import QuestionService
from app.services.report_service import ReportService
from app.services.followup_service import FollowUpService


USER_ID = uuid4()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class InMemoryExams:
    def __init__(self):
        self.rows: dict[UUID, dict] = {}

    def create(self, payload):
        sid = uuid4()
        row = {
            "id": str(sid),
            "user_id": payload["user_id"],
            "subject": payload["subject"],
            "topics": payload["topics"],
            "exam_mode": payload["exam_mode"],
            "initial_difficulty": payload["initial_difficulty"],
            "question_count": payload["question_count"],
            "status": payload["status"],
            "current_question_id": None,
            "started_at": None,
            "completed_at": None,
            "created_at": _now(),
            "updated_at": _now(),
        }
        self.rows[sid] = row
        return row

    def get_for_user(self, session_id, user_id):
        row = self.rows.get(UUID(str(session_id)))
        if not row or str(row["user_id"]) != str(user_id):
            return None
        return row.copy()

    def list_for_user(self, user_id, limit=50):
        return [
            row.copy() for row in self.rows.values()
            if str(row["user_id"]) == str(user_id)
        ][:limit]

    def update_for_user(self, session_id, user_id, payload):
        row = self.rows[UUID(str(session_id))]
        if str(row["user_id"]) != str(user_id):
            raise LookupError("Exam session not found.")
        row.update(payload)
        row["updated_at"] = _now()
        return row.copy()

    def count_questions(self, session_id):
        return sum(
            1
            for row in GLOBAL.questions.rows
            if str(row["exam_session_id"]) == str(session_id)
            and not row.get("is_follow_up", False)
        )

    def set_current_question(self, session_id, user_id, question_id):
        return self.update_for_user(
            session_id, user_id, {"current_question_id": str(question_id)}
        )

    def clear_current_question(self, session_id, user_id):
        return self.update_for_user(
            session_id, user_id, {"current_question_id": None}
        )

    def start(self, session_id, user_id):
        return self.update_for_user(
            session_id, user_id,
            {"status": "in_progress", "started_at": _now()},
        )

    def complete(self, session_id, user_id):
        return self.update_for_user(
            session_id, user_id,
            {"status": "completed", "completed_at": _now(), "current_question_id": None},
        )


class InMemoryQuestions:
    def __init__(self):
        self.rows: list[dict] = []

    def create_and_ask(self, payload):
        row = {
            "id": str(uuid4()),
            "created_at": _now(),
            "answered_at": None,
            **payload,
        }
        row["status"] = "asked"
        self.rows.append(row)
        return row.copy()

    def get_for_session(self, question_id, session_id):
        for row in self.rows:
            if str(row["id"]) == str(question_id) and str(row["exam_session_id"]) == str(session_id):
                return row.copy()
        return None

    def get_current(self, session_id):
        current = [
            row for row in self.rows
            if str(row["exam_session_id"]) == str(session_id)
            and row.get("status") == "asked"
        ]
        return current[-1].copy() if current else None

    def list_for_session(self, session_id):
        rows = [
            row.copy() for row in self.rows
            if str(row["exam_session_id"]) == str(session_id)
        ]
        return sorted(rows, key=lambda row: row["sequence_number"])

    def get_latest_sequence(self, session_id):
        rows = self.list_for_session(session_id)
        return max([int(row["sequence_number"]) for row in rows] or [0])

    def mark_answered(self, question_id, session_id):
        row = self.get_for_session(question_id, session_id)
        row["status"] = "answered"
        row["answered_at"] = _now()
        for existing in self.rows:
            if existing["id"] == row["id"]:
                existing.update(row)
        return row


class InMemoryAnswers:
    def __init__(self):
        self.rows: list[dict] = []

    def create(self, payload):
        row = {"id": str(uuid4()), "submitted_at": _now(), **payload}
        self.rows.append(row)
        return row.copy()

    def get_for_question_and_user(self, question_id, user_id):
        for row in self.rows:
            if str(row["question_id"]) == str(question_id) and str(row["user_id"]) == str(user_id):
                return row.copy()
        return None

    def list_for_session(self, session_id):
        return [
            row.copy() for row in self.rows
            if str(row["exam_session_id"]) == str(session_id)
        ]

    def list_for_question(self, question_id):
        return [
            row.copy() for row in self.rows
            if str(row["question_id"]) == str(question_id)
        ]


class InMemoryEvaluations:
    def __init__(self):
        self.rows: list[dict] = []

    def create(self, payload):
        row = {"id": str(uuid4()), "created_at": _now(), **payload}
        self.rows.append(row)
        return row.copy()

    def get_for_answer(self, answer_id):
        for row in self.rows:
            if str(row["answer_id"]) == str(answer_id):
                return row.copy()
        return None

    def list_for_answer_ids(self, answer_ids):
        allowed = {str(v) for v in answer_ids}
        return [row.copy() for row in self.rows if str(row["answer_id"]) in allowed]


class InMemoryKnowledge:
    def __init__(self):
        self.rows: dict[str, dict] = {}

    def upsert(self, payload):
        key = f'{payload["exam_session_id"]}:{payload["topic"].casefold()}'
        existing = self.rows.get(key, {})
        row = {**existing, "id": existing.get("id", str(uuid4())), **payload}
        self.rows[key] = row
        return row.copy()

    def list_for_session(self, session_id):
        return [row.copy() for row in self.rows.values() if str(row["exam_session_id"]) == str(session_id)]


class InMemoryPerformance:
    def __init__(self):
        self.rows: dict[str, dict] = {}

    def upsert(self, payload):
        key = f'{payload["exam_session_id"]}:{payload["topic"].casefold()}'
        existing = self.rows.get(key, {})
        row = {**existing, "id": existing.get("id", str(uuid4())), **payload}
        self.rows[key] = row
        return row.copy()

    def list_for_session(self, session_id):
        return [row.copy() for row in self.rows.values() if str(row["exam_session_id"]) == str(session_id)]


class InMemoryDocuments:
    def list_for_user(self, user_id):
        return []


class InMemoryReports:
    def __init__(self):
        self.rows: dict[str, dict] = {}

    def get_for_session(self, session_id, user_id):
        row = self.rows.get(str(session_id))
        if row and str(row["user_id"]) == str(user_id):
            return row.copy()
        return None

    def upsert(self, payload):
        existing = self.rows.get(str(payload["exam_session_id"]))
        row = {
            "id": existing["id"] if existing else str(uuid4()),
            "created_at": existing["created_at"] if existing else _now(),
            **payload,
        }
        self.rows[str(payload["exam_session_id"])] = row
        return row.copy()


class FakeGemini:
    def __init__(self):
        self.question_calls = 0
        self.evaluation_calls = 0
        self.grounded_calls = 0
        self.report_calls = 0

    def generate_grounded_text(self, prompt: str) -> GroundedTextResult:
        self.grounded_calls += 1
        return GroundedTextResult(
            text="Official context confirms the core technical definition.",
            sources=[
                {"title": "Authoritative technical reference", "url": "https://example.edu/reference"},
            ],
            searched=True,
        )

    def generate_structured(self, prompt: str, schema):
        if schema is QuestionGenerationResult:
            self.question_calls += 1
            is_followup = "Socratic follow-up" in prompt or "follow-up question" in prompt.lower()
            if is_followup:
                return QuestionGenerationResult(
                    question_text="What specific principle fixes the missing concept here?",
                    topic="SQL",
                    difficulty=3,
                    question_type="follow_up",
                    expected_points=["principle", "reasoning", "application"],
                )
            self.question_calls += 0
            topic = "SQL" if "question number: 1" in prompt.lower() else "Normalization"
            return QuestionGenerationResult(
                question_text=(
                    "Explain a primary key and why it matters in a relational schema."
                    if topic == "SQL"
                    else "Explain the purpose of normalization and one key normal form."
                ),
                topic=topic,
                difficulty=3,
                question_type="conceptual",
                expected_points=["definition", "purpose", "example"],
            )

        if schema is AnswerEvaluationResult:
            self.evaluation_calls += 1
            if self.evaluation_calls == 1:
                return AnswerEvaluationResult(
                    score=4.0, correctness=0.45, completeness=0.40,
                    conceptual_understanding=0.45, strengths=["basic definition"],
                    missing_concepts=["normalization rationale"],
                    misconceptions=[],
                    feedback="You have the foundation, but the explanation needs more depth.",
                )
            return AnswerEvaluationResult(
                score=9.0, correctness=0.95, completeness=0.95,
                conceptual_understanding=0.90, strengths=["clear reasoning"],
                missing_concepts=[], misconceptions=[],
                feedback="Strong explanation.",
            )

        if schema is FinalReportContent:
            self.report_calls += 1
            return FinalReportContent(
                summary="Strong overall performance with a clear improvement after targeted probing.",
                strong_areas=["SQL"],
                weak_areas=["Normalization"],
                concepts_to_revise=["normalization rationale"],
                recommendations=["Review normalization examples and trade-offs."],
                closing_feedback="Good work. Continue practicing explanation depth.",
            )

        raise AssertionError(f"Unexpected schema: {schema}")


class Bundle:
    def __init__(self):
        self.exams = InMemoryExams()
        self.questions = InMemoryQuestions()
        self.answers = InMemoryAnswers()
        self.evaluations = InMemoryEvaluations()
        self.knowledge = InMemoryKnowledge()
        self.performance = InMemoryPerformance()
        self.documents = InMemoryDocuments()
        self.reports = InMemoryReports()

    def as_dict(self):
        return {
            "exams": self.exams,
            "questions": self.questions,
            "answers": self.answers,
            "evaluations": self.evaluations,
            "knowledge": self.knowledge,
            "performance": self.performance,
            "documents": self.documents,
            "reports": self.reports,
        }


GLOBAL: Bundle


@pytest.fixture
def client_and_bundle():
    global GLOBAL
    GLOBAL = Bundle()
    repos = GLOBAL.as_dict()
    gemini = FakeGemini()

    exam_service = ExamService(
        repositories=repos,
        question_service=QuestionService(repositories=repos, gemini=gemini),
        report_service=ReportService(repositories=repos, gemini=gemini),
    )
    evaluation_service = EvaluationService(repositories=repos, gemini=gemini)
    conversation_service = ConversationService(
        repositories=repos,
        evaluation_service=evaluation_service,
        question_service=exam_service.question_service,
        followup_service=FollowUpService(repositories=repos, gemini=gemini),
    )
    report_service = ReportService(repositories=repos, gemini=gemini)
    knowledge_service = KnowledgeStateService(repositories=repos)

    app.dependency_overrides[get_current_user_id] = lambda: USER_ID
    app.dependency_overrides[get_exam_service] = lambda: exam_service
    app.dependency_overrides[get_evaluation_service] = lambda: evaluation_service
    app.dependency_overrides[get_conversation_service] = lambda: conversation_service
    app.dependency_overrides[get_report_service] = lambda: report_service
    app.dependency_overrides[get_knowledge_service] = lambda: knowledge_service

    try:
        yield TestClient(app), GLOBAL, gemini
    finally:
        app.dependency_overrides.clear()


@pytest.mark.e2e
def test_full_conversational_exam_to_report(client_and_bundle):
    client, bundle, gemini = client_and_bundle

    create = client.post(
        "/api/exams",
        headers={"Authorization": "Bearer test-token"},
        json={
            "subject": "Database Systems",
            "topics": ["SQL", "Normalization"],
            "exam_mode": "viva",
            "difficulty": 3,
            "question_count": 2,
        },
    )
    assert create.status_code == 201
    session_id = create.json()["id"]
    assert create.json()["status"] == "created"

    start = client.post(
        f"/api/exams/{session_id}/start",
        headers={"Authorization": "Bearer test-token"},
    )
    assert start.status_code == 200
    first = start.json()["question"]
    assert first["question_type"] == "conceptual"
    assert first["topic"] == "SQL"

    first_turn = client.post(
        f"/api/exams/{session_id}/chat/turn",
        headers={"Authorization": "Bearer test-token"},
        json={"question_id": first["id"], "answer_text": "A primary key identifies a row."},
    )
    assert first_turn.status_code == 200
    first_payload = first_turn.json()
    assert first_payload["next_question"]["is_follow_up"] is True
    assert first_payload["exam_completed"] is False
    assert "probe" in first_payload["examiner_message"].lower()

    followup_id = first_payload["next_question"]["id"]
    followup_turn = client.post(
        f"/api/exams/{session_id}/chat/turn",
        headers={"Authorization": "Bearer test-token"},
        json={"question_id": followup_id, "answer_text": "Normalization removes harmful redundancy."},
    )
    assert followup_turn.status_code == 200
    second = followup_turn.json()["next_question"]
    assert second is not None
    assert second["is_follow_up"] is False
    assert second["topic"] == "Normalization"

    second_turn = client.post(
        f"/api/exams/{session_id}/chat/turn",
        headers={"Authorization": "Bearer test-token"},
        json={"question_id": second["id"], "answer_text": "Normalization structures relations to reduce anomalies."},
    )
    assert second_turn.status_code == 200
    assert second_turn.json()["exam_completed"] is True
    assert second_turn.json()["next_question"] is None

    summary = client.get(
        f"/api/exams/{session_id}/performance-summary",
        headers={"Authorization": "Bearer test-token"},
    )
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload["configured_main_questions"] == 2
    assert summary_payload["answered_main_questions"] == 2
    assert summary_payload["follow_up_questions"] == 1
    assert summary_payload["evaluated_follow_up_answers"] == 1
    assert 0 < summary_payload["topic_coverage"] <= 1

    report = client.post(
        f"/api/exams/{session_id}/report",
        headers={"Authorization": "Bearer test-token"},
    )
    assert report.status_code == 200
    report_payload = report.json()
    assert report_payload["overall_score"] == 6.5
    assert report_payload["performance_snapshot"]["answered_main_questions"] == 2

    report_again = client.get(
        f"/api/exams/{session_id}/report",
        headers={"Authorization": "Bearer test-token"},
    )
    assert report_again.status_code == 200
    assert report_again.json()["id"] == report_payload["id"]
    assert gemini.report_calls == 1

    complete = client.post(
        f"/api/exams/{session_id}/complete",
        headers={"Authorization": "Bearer test-token"},
    )
    assert complete.status_code == 200
    assert complete.json()["session"]["status"] == "completed"
    assert gemini.grounded_calls >= 5


@pytest.mark.e2e
def test_report_cannot_be_generated_before_all_main_answers(client_and_bundle):
    client, _, _ = client_and_bundle
    create = client.post(
        "/api/exams",
        headers={"Authorization": "Bearer test-token"},
        json={
            "subject": "Database Systems",
            "topics": ["SQL"],
            "exam_mode": "viva",
            "difficulty": 2,
            "question_count": 1,
        },
    )
    session_id = create.json()["id"]
    response = client.post(
        f"/api/exams/{session_id}/report",
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 409
    assert "final report requires" in response.json()["detail"].lower()


@pytest.mark.e2e
def test_chat_turn_rejects_non_current_question(client_and_bundle):
    client, _, _ = client_and_bundle
    create = client.post(
        "/api/exams",
        headers={"Authorization": "Bearer test-token"},
        json={
            "subject": "Database Systems",
            "topics": ["SQL"],
            "exam_mode": "viva",
            "difficulty": 3,
            "question_count": 1,
        },
    )
    session_id = create.json()["id"]
    start = client.post(
        f"/api/exams/{session_id}/start",
        headers={"Authorization": "Bearer test-token"},
    )
    qid = start.json()["question"]["id"]
    fake_id = str(uuid4())
    response = client.post(
        f"/api/exams/{session_id}/chat/turn",
        headers={"Authorization": "Bearer test-token"},
        json={"question_id": fake_id, "answer_text": "answer"},
    )
    assert response.status_code == 404
    assert "question" in response.json()["detail"].lower()


@pytest.mark.e2e
def test_unauthenticated_request_is_rejected():
    response = TestClient(app).get("/api/exams")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing bearer access token."
