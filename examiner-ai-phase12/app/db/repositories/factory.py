from functools import lru_cache

from app.db.repositories.answer_repository import AnswerRepository
from app.db.repositories.document_repository import DocumentRepository
from app.db.repositories.evaluation_repository import EvaluationRepository
from app.db.repositories.exam_repository import ExamRepository
from app.db.repositories.knowledge_repository import KnowledgeRepository
from app.db.repositories.performance_repository import PerformanceRepository
from app.db.repositories.question_repository import QuestionRepository
from app.db.repositories.report_repository import ReportRepository
from app.db.supabase import get_supabase_client


@lru_cache
def get_repositories():
    client = get_supabase_client()
    return {
        "exams": ExamRepository(client),
        "questions": QuestionRepository(client),
        "answers": AnswerRepository(client),
        "evaluations": EvaluationRepository(client),
        "knowledge": KnowledgeRepository(client),
        "performance": PerformanceRepository(client),
        "documents": DocumentRepository(client),
        "reports": ReportRepository(client),
    }
