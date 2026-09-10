from uuid import uuid4

from app.models.enums import EvaluationDecision
from app.schemas.domain import EvaluationRecord
from app.services.knowledge_service import KnowledgeStateService


class FakeExams:
    def __init__(self, user_id, session_id):
        self.user_id = user_id
        self.session_id = session_id

    def get_for_user(self, session_id, user_id):
        if session_id == self.session_id and user_id == self.user_id:
            return {"id": session_id, "user_id": user_id}
        return None


class FakeKnowledge:
    def __init__(self):
        self.rows = {}

    def list_for_session(self, session_id):
        return list(self.rows.values())

    def upsert(self, payload):
        key = (payload["exam_session_id"], payload["topic"].casefold())
        row = {"id": str(uuid4()), **payload}
        self.rows[key] = row
        return row


class FakePerformance:
    def __init__(self):
        self.rows = {}

    def list_for_session(self, session_id):
        return list(self.rows.values())

    def upsert(self, payload):
        key = (payload["exam_session_id"], payload["topic"].casefold())
        row = {"id": str(uuid4()), **payload}
        self.rows[key] = row
        return row


def evaluation(
    score=8.0,
    correctness=0.9,
    completeness=0.8,
    conceptual=0.85,
    strengths=None,
    missing=None,
    misconceptions=None,
):
    return EvaluationRecord(
        id=uuid4(),
        answer_id=uuid4(),
        question_id=uuid4(),
        score=score,
        correctness=correctness,
        completeness=completeness,
        conceptual_understanding=conceptual,
        strengths=strengths or [],
        missing_concepts=missing or [],
        misconceptions=misconceptions or [],
        feedback="Feedback",
        decision=EvaluationDecision.NEXT,
        created_at="2026-09-10T12:00:00Z",
    )


def setup():
    user_id, session_id = uuid4(), uuid4()
    knowledge = FakeKnowledge()
    performance = FakePerformance()
    repos = {
        "exams": FakeExams(user_id, session_id),
        "knowledge": knowledge,
        "performance": performance,
    }
    return (
        KnowledgeStateService(repositories=repos),
        user_id,
        session_id,
        knowledge,
        performance,
    )


def test_first_evaluation_creates_topic_knowledge_and_performance():
    service, user_id, session_id, knowledge, performance = setup()
    ks, tp = service.process_evaluation(
        user_id,
        session_id,
        "Normalization",
        evaluation(
            strengths=["2NF", "2NF"],
            missing=["Transitive dependency"],
            misconceptions=["Confuses 2NF and 3NF"],
        ),
        3,
    )

    assert ks.topic == "Normalization"
    assert ks.attempts == 1
    assert 0 < ks.mastery_score < 1
    assert ks.strong_concepts == ["2NF"]
    assert ks.weak_concepts == ["Transitive dependency", "Confuses 2NF and 3NF"]
    assert ks.misconceptions == ["Confuses 2NF and 3NF"]

    assert tp.questions_attempted == 1
    assert tp.average_score == 8.0
    assert tp.accuracy == 0.9


def test_second_evaluation_updates_running_averages_and_mastery():
    service, user_id, session_id, knowledge, performance = setup()

    service.process_evaluation(
        user_id,
        session_id,
        "SQL",
        evaluation(score=6, correctness=0.6, completeness=0.5, conceptual=0.5),
        3,
    )
    ks, tp = service.process_evaluation(
        user_id,
        session_id,
        "SQL",
        evaluation(
            score=10,
            correctness=1,
            completeness=1,
            conceptual=1,
            strengths=["Joins"],
        ),
        4,
    )

    assert ks.attempts == 2
    assert round(ks.mastery_score, 4) == round(((0.6 * 0.45 + 0.5 * 0.30 + 0.5 * 0.25) + 1) / 2, 4)
    assert tp.questions_attempted == 2
    assert tp.average_score == 8.0
    assert tp.accuracy == 0.8
    assert ks.strong_concepts == ["Joins"]


def test_weak_concepts_are_removed_when_later_marked_strong():
    service, user_id, session_id, knowledge, performance = setup()

    service.process_evaluation(
        user_id,
        session_id,
        "Transactions",
        evaluation(
            score=3,
            correctness=0.3,
            completeness=0.2,
            conceptual=0.2,
            missing=["Isolation"],
        ),
        2,
    )
    ks, _ = service.process_evaluation(
        user_id,
        session_id,
        "Transactions",
        evaluation(
            score=9,
            correctness=0.95,
            completeness=0.9,
            conceptual=0.9,
            strengths=["Isolation"],
        ),
        2,
    )

    assert "Isolation" in ks.strong_concepts
    assert "Isolation" not in ks.weak_concepts


def test_knowledge_queries_are_user_scoped():
    service, user_id, session_id, knowledge, performance = setup()
    service.process_evaluation(
        user_id,
        session_id,
        "DBMS",
        evaluation(),
        3,
    )

    assert len(service.list_knowledge_states(user_id, session_id)) == 1
    assert len(service.list_topic_performance(user_id, session_id)) == 1
