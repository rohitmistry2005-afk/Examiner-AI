
from uuid import uuid4
from app.services.adaptive_service import AdaptiveEngine

class E:
    def __init__(self, row): self.row=row
    def get_for_user(self, sid, uid): return self.row

class Q:
    def __init__(self, rows): self.rows=rows
    def list_for_session(self, sid): return self.rows

class K:
    def __init__(self, rows): self.rows=rows
    def list_for_session(self, sid): return self.rows

class P:
    def __init__(self, rows): self.rows=rows
    def list_for_session(self, sid): return self.rows

def session(uid, sid, topics=("SQL","Normalization"), diff=3):
    return {
        "id": str(sid), "user_id": str(uid), "subject": "DBMS",
        "topics": list(topics), "exam_mode": "semester",
        "initial_difficulty": diff, "question_count": 10,
        "status": "in_progress", "current_question_id": None,
        "started_at": "2026-09-10T12:00:00Z", "completed_at": None,
        "created_at": "2026-09-10T12:00:00Z", "updated_at": "2026-09-10T12:00:00Z"
    }

def qrow(sid, topic, seq):
    return {
        "id": str(uuid4()), "exam_session_id": str(sid), "parent_question_id": None,
        "topic": topic, "difficulty": 3, "question_type": "conceptual",
        "question_text": f"Question {seq}", "expected_points": ["A","B","C"],
        "status": "answered", "sequence_number": seq, "is_follow_up": False,
        "created_at": "2026-09-10T12:00:00Z", "answered_at": "2026-09-10T12:01:00Z"
    }

def krow(sid, uid, topic, mastery, diff):
    return {
        "id": str(uuid4()), "user_id": str(uid), "exam_session_id": str(sid),
        "topic": topic, "mastery_score": mastery, "current_difficulty": diff,
        "strong_concepts": [], "weak_concepts": [], "misconceptions": [],
        "attempts": 2, "updated_at": "2026-09-10T12:00:00Z"
    }

def prow(sid, uid, topic, acc):
    return {
        "id": str(uuid4()), "user_id": str(uid), "exam_session_id": str(sid),
        "topic": topic, "questions_attempted": 2, "average_score": acc*10,
        "accuracy": acc, "updated_at": "2026-09-10T12:00:00Z"
    }

def repos(uid, sid, questions, knowledge, performance, difficulty=3):
    return {
        "exams": E(session(uid, sid, diff=difficulty)),
        "questions": Q(questions),
        "knowledge": K(knowledge),
        "performance": P(performance),
    }

def test_uncovered_topic_is_prioritized():
    uid, sid = uuid4(), uuid4()
    r = repos(uid, sid, [qrow(sid,"SQL",1)],
              [krow(sid,uid,"SQL",0.9,4)],
              [prow(sid,uid,"SQL",0.9)])
    d = AdaptiveEngine(r).select_next(uid,sid)
    assert (d.target_topic, d.action, d.difficulty) == ("Normalization","advance",3)

def test_weak_topic_decreases_difficulty():
    uid, sid = uuid4(), uuid4()
    qs=[qrow(sid,"SQL",1),qrow(sid,"Normalization",2)]
    r=repos(uid,sid,qs,
            [krow(sid,uid,"SQL",0.8,3),krow(sid,uid,"Normalization",0.25,2)],
            [prow(sid,uid,"SQL",0.8),prow(sid,uid,"Normalization",0.3)])
    d=AdaptiveEngine(r).select_next(uid,sid)
    assert (d.target_topic,d.action,d.difficulty)==("Normalization","decrease_difficulty",1)

def test_strong_topic_increases_difficulty():
    uid,sid=uuid4(),uuid4()
    qs=[qrow(sid,"SQL",1),qrow(sid,"Normalization",2)]
    r=repos(uid,sid,qs,
            [krow(sid,uid,"SQL",0.85,4),krow(sid,uid,"Normalization",0.95,4)],
            [prow(sid,uid,"SQL",0.85),prow(sid,uid,"Normalization",0.95)])
    d=AdaptiveEngine(r).select_next(uid,sid)
    assert d.action=="increase_difficulty"
    assert d.difficulty==5

def test_moderate_topic_maintains_difficulty():
    uid,sid=uuid4(),uuid4()
    qs=[qrow(sid,"SQL",1),qrow(sid,"Normalization",2)]
    r=repos(uid,sid,qs,
            [krow(sid,uid,"SQL",0.65,3),krow(sid,uid,"Normalization",0.60,3)],
            [prow(sid,uid,"SQL",0.65),prow(sid,uid,"Normalization",0.60)])
    d=AdaptiveEngine(r).select_next(uid,sid)
    assert d.action=="maintain" and d.difficulty==3

def test_legacy_doubles_fall_back_to_phase4_rotation():
    uid,sid=uuid4(),uuid4()
    r={"exams":E(session(uid,sid,diff=4)),"questions":Q([qrow(sid,"SQL",1)])}
    d=AdaptiveEngine(r).select_next(uid,sid)
    assert d.target_topic=="Normalization" and d.difficulty==4
