from uuid import UUID, uuid4
from types import SimpleNamespace

import pytest

from app.models.enums import QuestionType, EvaluationDecision
from app.schemas.ai import AnswerEvaluationResult, QuestionGenerationResult
from app.services.evaluation_service import EvaluationService


class FakeExams:
    def __init__(self):
        self.row = None
        self.cleared = []

    def get_for_user(self, session_id, user_id):
        return self.row

    def clear_current_question(self, session_id, user_id):
        self.cleared.append((session_id, user_id))
        self.row["current_question_id"] = None
        return self.row


class FakeQuestions:
    def __init__(self):
        self.row = None
        self.answered = []

    def get_for_session(self, question_id, session_id):
        return self.row

    def mark_answered(self, question_id, session_id):
        self.row["status"] = "answered"
        self.answered.append((question_id, session_id))
        return self.row


class FakeAnswers:
    def __init__(self):
        self.row = None
        self.created = []

    def get_for_question_and_user(self, question_id, user_id):
        return self.row

    def create(self, payload):
        self.row = {"id": uuid4(), **payload, "submitted_at": "2026-09-10T12:00:00Z"}
        self.created.append(self.row)
        return self.row


class FakeEvaluations:
    def __init__(self):
        self.row = None

    def get_for_answer(self, answer_id):
        return self.row

    def create(self, payload):
        self.row = {"id": uuid4(), **payload, "created_at": "2026-09-10T12:00:01Z"}
        return self.row


class FakeGemini:
    def __init__(self):
        self.prompts = []
        self.result = AnswerEvaluationResult(
            score=7.5,
            correctness=0.8,
            completeness=0.7,
            conceptual_understanding=0.75,
            strengths=["Correct core idea"],
            missing_concepts=["Transitive dependency"],
            misconceptions=[],
            feedback="Good explanation, but one key concept is missing.",
        )

    def generate_structured(self, prompt, schema):
        assert schema is AnswerEvaluationResult
        self.prompts.append(prompt)
        return self.result


def setup():
    user_id, session_id, question_id = uuid4(), uuid4(), uuid4()
    exams = FakeExams()
    exams.row = {
        "id": session_id,
        "user_id": str(user_id),
        "subject": "DBMS",
        "exam_mode": "semester",
        "status": "in_progress",
        "current_question_id": str(question_id),
    }
    questions = FakeQuestions()
    questions.row = {
        "id": question_id,
        "exam_session_id": session_id,
        "parent_question_id": None,
        "topic": "Normalization",
        "difficulty": 3,
        "question_type": "conceptual",
        "question_text": "Explain third normal form.",
        "expected_points": ["2NF prerequisite", "Transitive dependency", "Non-prime attributes"],
        "status": "asked",
        "sequence_number": 1,
        "is_follow_up": False,
        "created_at": "2026-09-10T11:00:00Z",
        "answered_at": None,
    }
    answers, evaluations, gemini = FakeAnswers(), FakeEvaluations(), FakeGemini()
    repos = {
        "exams": exams,
        "questions": questions,
        "answers": answers,
        "evaluations": evaluations,
    }
    service = EvaluationService(repositories=repos, gemini=gemini)
    return service, exams, questions, answers, evaluations, gemini, user_id, session_id, question_id


def test_submit_answer_persists_and_evaluates():
    service, exams, questions, answers, evaluations, gemini, user_id, session_id, question_id = setup()
    answer, evaluation = service.submit_answer(
        user_id, session_id, question_id, "  It removes transitive dependency issues.  "
    )

    assert answer.answer_text == "It removes transitive dependency issues."
    assert evaluation.score == 7.5
    assert evaluation.decision == EvaluationDecision.NEXT
    assert len(gemini.prompts) == 1
    assert questions.row["status"] == "answered"
    assert exams.row["current_question_id"] is None


def test_existing_evaluated_answer_is_idempotently_reused():
    service, exams, questions, answers, evaluations, gemini, user_id, session_id, question_id = setup()
    answer_row = answers.create({
        "question_id": str(question_id),
        "exam_session_id": str(session_id),
        "user_id": str(user_id),
        "answer_text": "Existing answer",
    })
    evaluation_row = evaluations.create({
        "answer_id": str(answer_row["id"]),
        "question_id": str(question_id),
        "score": 8,
        "correctness": 0.9,
        "completeness": 0.8,
        "conceptual_understanding": 0.85,
        "strengths": ["Strong"],
        "missing_concepts": [],
        "misconceptions": [],
        "feedback": "Good.",
        "decision": "next",
    })

    reused_answer, reused_eval = service.submit_answer(
        user_id, session_id, question_id, "Ignored duplicate"
    )
    assert reused_answer.id == answer_row["id"]
    assert reused_eval.id == evaluation_row["id"]
    assert len(gemini.prompts) == 0


def test_only_current_question_can_be_answered():
    service, exams, questions, answers, evaluations, gemini, user_id, session_id, question_id = setup()
    exams.row["current_question_id"] = str(uuid4())
    with pytest.raises(ValueError, match="current question"):
        service.submit_answer(user_id, session_id, question_id, "Answer")


def test_answer_requires_in_progress_session():
    service, exams, questions, answers, evaluations, gemini, user_id, session_id, question_id = setup()
    exams.row["status"] = "completed"
    with pytest.raises(ValueError, match="in-progress"):
        service.submit_answer(user_id, session_id, question_id, "Answer")
