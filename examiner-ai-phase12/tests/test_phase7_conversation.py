
from uuid import uuid4
from app.models.enums import EvaluationDecision, QuestionStatus, QuestionType
from app.schemas.ai import AdaptiveDecisionResult
from app.schemas.domain import AnswerRecord, EvaluationRecord, QuestionRecord
from app.services.conversation_service import ConversationService

class E:
    def __init__(self,sid,uid,count):
        self.sid = sid
        self.uid = uid
        self.configured_count = count
        self.persisted_main_count = count if count == 1 else 1

    def get_for_user(self,sid,uid):
        return {"id":str(sid),"user_id":str(uid),"subject":"DBMS",
                "topics":["SQL","Normalization"],"question_count":self.configured_count,
                "status":"in_progress"}

    def count_questions(self,sid):
        return self.persisted_main_count

class Eval:
    def __init__(self,sid,uid,qid):
        self.a=AnswerRecord(id=uuid4(),question_id=qid,exam_session_id=sid,user_id=uid,
                            answer_text="answer",submitted_at="2026-09-10T12:01:00Z")
        self.e=EvaluationRecord(id=uuid4(),answer_id=self.a.id,question_id=qid,score=7,
                                correctness=.8,completeness=.7,conceptual_understanding=.8,
                                strengths=["Core"],missing_concepts=["Isolation"],
                                misconceptions=[],feedback="Good answer.",
                                decision=EvaluationDecision.NEXT,
                                created_at="2026-09-10T12:01:00Z")
    def submit_answer(self,**kwargs): return self.a,self.e

class A:
    def select_next(self,uid,sid):
        return AdaptiveDecisionResult(action="maintain",target_topic="SQL",difficulty=3,reason="Continue.")

class Questions:
    def get_for_session(self, qid, sid):
        return {
            "id": str(qid), "exam_session_id": str(sid),
            "parent_question_id": None, "topic": "SQL", "difficulty": 3,
            "question_type": "conceptual", "question_text": "Explain SQL joins.",
            "expected_points": ["join", "tables", "relationship"],
            "status": "asked", "sequence_number": 1, "is_follow_up": False,
            "created_at": "2026-09-10T12:00:00Z", "answered_at": None,
        }

class Q:
    def generate_next_main_question(self,uid,sid):
        return QuestionRecord(id=uuid4(),exam_session_id=sid,parent_question_id=None,
                              topic="SQL",difficulty=3,question_type=QuestionType.CONCEPTUAL,
                              question_text="What is a primary key?",
                              expected_points=["unique","identify","row"],
                              status=QuestionStatus.ASKED,sequence_number=2,
                              is_follow_up=False,created_at="2026-09-10T12:02:00Z",
                              answered_at=None)

def setup(count):
    uid,sid,qid=uuid4(),uuid4(),uuid4()
    repos={"exams":E(sid,uid,count), "questions": Questions()}
    class NoFollowUp:
        def create_follow_up(self, *args, **kwargs):
            return None
    svc=ConversationService(repositories=repos,
                            evaluation_service=Eval(sid,uid,qid),
                            question_service=Q(),
                            adaptive_engine=A(),
                            followup_service=NoFollowUp())
    return svc,uid,sid,qid

def test_chat_turn_returns_examiner_turn():
    svc,uid,sid,qid=setup(2)
    r=svc.submit_turn(uid,sid,qid,"student")
    assert not r.exam_completed
    assert r.next_question is not None
    assert "Good answer." in r.examiner_message
    assert "What is a primary key?" in r.examiner_message

def test_chat_turn_closes_after_last_question():
    svc,uid,sid,qid=setup(1)
    r=svc.submit_turn(uid,sid,qid,"student")
    assert r.exam_completed
    assert r.next_question is None
    assert "completes the configured examination" in r.examiner_message
