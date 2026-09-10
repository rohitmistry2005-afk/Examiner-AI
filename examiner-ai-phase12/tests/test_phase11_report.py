from datetime import datetime, timezone
from uuid import uuid4

from app.models.enums import EvaluationDecision, ExamMode, QuestionStatus, QuestionType, ExamSessionStatus
from app.schemas.ai import FinalReportContent
from app.services.report_service import ReportService


NOW = datetime.now(timezone.utc)


def session(uid, sid, status="completed"):
    return {
        "id": str(sid), "user_id": str(uid), "subject": "Computer Networks",
        "topics": ["TCP", "Routing"], "exam_mode": "technical_test", "initial_difficulty": 3,
        "question_count": 2, "status": status, "current_question_id": None,
        "started_at": NOW.isoformat(), "completed_at": NOW.isoformat(),
        "created_at": NOW.isoformat(), "updated_at": NOW.isoformat(),
    }


def question(sid, qid, topic, follow=False, seq=1):
    return {
        "id": str(qid), "exam_session_id": str(sid), "parent_question_id": None,
        "topic": topic, "difficulty": 3,
        "question_type": "follow_up" if follow else "conceptual",
        "question_text": f"Explain {topic}", "expected_points": ["a", "b", "c"],
        "status": "answered", "sequence_number": seq, "is_follow_up": follow,
        "created_at": NOW.isoformat(), "answered_at": NOW.isoformat(),
    }


def answer(sid, qid, aid, uid):
    return {
        "id": str(aid), "question_id": str(qid), "exam_session_id": str(sid), "user_id": str(uid),
        "answer_text": "answer", "submitted_at": NOW.isoformat(),
    }


def evaluation(aid, qid, score, correctness, completeness, conceptual, missing=None, misconceptions=None):
    return {
        "id": str(uuid4()), "answer_id": str(aid), "question_id": str(qid),
        "score": score, "correctness": correctness, "completeness": completeness,
        "conceptual_understanding": conceptual, "strengths": ["clear reasoning"],
        "missing_concepts": missing or [], "misconceptions": misconceptions or [],
        "feedback": "Good work", "decision": "next", "created_at": NOW.isoformat(),
    }


class Repo:
    def __init__(self, rows=None): self.rows = rows or []
    def list_for_session(self, sid): return self.rows


class Exams:
    def __init__(self, row): self.row = row
    def get_for_user(self, sid, uid): return self.row


class Answers:
    def __init__(self, rows): self.rows = rows
    def list_for_session(self, sid): return self.rows


class Evaluations:
    def __init__(self, rows): self.rows = rows
    def list_for_answer_ids(self, ids): return self.rows


class Reports:
    def __init__(self): self.row = None
    def get_for_session(self, sid, uid): return self.row
    def upsert(self, payload):
        self.row = {
            "id": str(uuid4()), "created_at": NOW.isoformat(), **payload,
        }
        return self.row


class Gemini:
    def generate_structured(self, prompt, schema):
        assert schema is FinalReportContent
        assert "Performance evidence:" in prompt
        return FinalReportContent(
            summary="Strong performance with one revision area.",
            strong_areas=["TCP"], weak_areas=["Routing"],
            concepts_to_revise=["Routing tables"],
            recommendations=["Practice routing scenarios."],
            closing_feedback="Keep applying the concepts to realistic problems.",
        )


def setup():
    uid, sid = uuid4(), uuid4()
    q1, q2, q3 = uuid4(), uuid4(), uuid4()
    a1, a2, a3 = uuid4(), uuid4(), uuid4()
    questions = Repo([
        question(sid, q1, "TCP", False, 1),
        question(sid, q2, "Routing", False, 2),
        question(sid, q3, "Routing", True, 3),
    ])
    answers = Answers([
        answer(sid, q1, a1, uid), answer(sid, q2, a2, uid), answer(sid, q3, a3, uid)
    ])
    evaluations = Evaluations([
        evaluation(a1, q1, 9, .9, .9, .9),
        evaluation(a2, q2, 5, .5, .4, .4, ["Routing tables"], ["Route selection"]),
        evaluation(a3, q3, 4, .4, .3, .3, ["CIDR"], ["Route selection"]),
    ])
    knowledge = Repo([
        {"id": str(uuid4()), "user_id": str(uid), "exam_session_id": str(sid), "topic": "TCP",
         "mastery_score": .88, "current_difficulty": 4, "strong_concepts": ["Reliability"],
         "weak_concepts": [], "misconceptions": [], "attempts": 1, "updated_at": NOW.isoformat()},
        {"id": str(uuid4()), "user_id": str(uid), "exam_session_id": str(sid), "topic": "Routing",
         "mastery_score": .34, "current_difficulty": 2, "strong_concepts": [],
         "weak_concepts": ["Routing tables", "CIDR"], "misconceptions": ["Route selection"],
         "attempts": 2, "updated_at": NOW.isoformat()},
    ])
    performance = Repo([
        {"id": str(uuid4()), "user_id": str(uid), "exam_session_id": str(sid), "topic": "TCP",
         "questions_attempted": 1, "average_score": 9, "accuracy": .9, "updated_at": NOW.isoformat()},
        {"id": str(uuid4()), "user_id": str(uid), "exam_session_id": str(sid), "topic": "Routing",
         "questions_attempted": 2, "average_score": 4.5, "accuracy": .45, "updated_at": NOW.isoformat()},
    ])
    reports = Reports()
    repos = {"exams": Exams(session(uid, sid)), "questions": questions, "answers": answers,
             "evaluations": evaluations, "knowledge": knowledge, "performance": performance,
             "reports": reports}
    return ReportService(repositories=repos, gemini=Gemini()), uid, sid, reports


def test_build_performance_summary_separates_followups_from_main_score():
    service, uid, sid, _ = setup()
    summary = service.build_performance_summary(uid, sid)

    assert summary.overall_score == 7.0
    assert summary.configured_main_questions == 2
    assert summary.answered_main_questions == 2
    assert summary.follow_up_questions == 1
    assert summary.evaluated_answers == 3
    assert summary.evaluated_follow_up_answers == 1
    assert summary.topic_coverage == 1.0
    assert summary.strong_topics == ["TCP"]
    assert summary.weak_topics == ["Routing"]
    assert "Route selection" in summary.misconceptions


def test_generate_report_persists_snapshot_and_is_idempotent():
    service, uid, sid, reports = setup()
    first = service.generate_report(uid, sid)
    second = service.generate_report(uid, sid)

    assert first.id == second.id
    assert first.overall_score == 7.0
    assert first.performance_snapshot["answered_main_questions"] == 2
    assert first.weak_areas == ["Routing"]
    assert reports.row is not None


def test_exam_completion_generates_report_before_status_transition():
    from app.services.exam_service import ExamService
    from app.schemas.domain import ExamCreateRequest

    uid, sid = uuid4(), uuid4()
    row = session(uid, sid, status="in_progress")
    exams = Exams(row)
    report_calls = []

    class ReportGate:
        def generate_report(self, user_id, session_id):
            report_calls.append((user_id, session_id, exams.row["status"]))
            return None

    class CompletingExams(Exams):
        def complete(self, session_id, user_id):
            self.row["status"] = "completed"
            return self.row

    exams = CompletingExams(row)
    service = ExamService(
        repositories={"exams": exams, "questions": Repo([])},
        report_service=ReportGate(),
    )

    result = service.complete_exam(uid, sid)
    assert result.session.status == ExamSessionStatus.COMPLETED
    assert report_calls == [(uid, sid, "in_progress")]


def test_final_report_rejects_partial_main_question_coverage():
    service, uid, sid, _ = setup()
    service.exams.row["question_count"] = 4
    try:
        service.generate_report(uid, sid)
        raise AssertionError("Expected incomplete exam report generation to fail")
    except ValueError as exc:
        assert "every configured main question" in str(exc)
