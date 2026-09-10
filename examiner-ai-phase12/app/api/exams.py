from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user_id
from app.schemas.domain import (
    CurrentQuestionResponse,
    ChatTurnRequest,
    ChatTurnResponse,
    ExamCompletionResponse,
    ExamCreateRequest,
    ExamSessionRecord,
    ExamStartResponse,
    QuestionRecord,
    AnswerSubmissionRequest,
    AnswerSubmissionResponse,
    KnowledgeStateRecord,
    TopicPerformanceRecord,
    PerformanceSummary,
    ReportRecord,
)
from app.services.exam_service import ExamService
from app.services.question_service import QuestionService
from app.services.evaluation_service import EvaluationService
from app.services.knowledge_service import KnowledgeStateService
from app.services.conversation_service import ConversationService
from app.services.report_service import ReportService

router = APIRouter(prefix="/exams", tags=["exams"])


def get_exam_service() -> ExamService:
    return ExamService(question_service=QuestionService(), report_service=ReportService())


def get_evaluation_service() -> EvaluationService:
    return EvaluationService()


def get_knowledge_service() -> KnowledgeStateService:
    return KnowledgeStateService()


def get_conversation_service() -> ConversationService:
    return ConversationService()


def get_report_service() -> ReportService:
    return ReportService()


def _http_error(exc: Exception) -> HTTPException:
    if isinstance(exc, LookupError):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, ValueError):
        return HTTPException(status_code=409, detail=str(exc))
    return HTTPException(status_code=500, detail="Unable to process the exam request.")


@router.post("", response_model=ExamSessionRecord, status_code=status.HTTP_201_CREATED)
def create_exam(
    request: ExamCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    service: ExamService = Depends(get_exam_service),
) -> ExamSessionRecord:
    try:
        return service.create_exam(user_id, request)
    except ValueError as exc:
        raise _http_error(exc) from exc
    except Exception as exc:
        raise _http_error(exc) from exc


@router.get("", response_model=list[ExamSessionRecord])
def list_exams(
    user_id: UUID = Depends(get_current_user_id),
    service: ExamService = Depends(get_exam_service),
) -> list[ExamSessionRecord]:
    try:
        return service.list_exams(user_id)
    except Exception as exc:
        raise _http_error(exc) from exc


@router.get(
    "/{session_id}/performance-summary",
    response_model=PerformanceSummary,
)
def get_performance_summary(
    session_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: ReportService = Depends(get_report_service),
) -> PerformanceSummary:
    try:
        return service.build_performance_summary(user_id, session_id)
    except Exception as exc:
        raise _http_error(exc) from exc


@router.post(
    "/{session_id}/report",
    response_model=ReportRecord,
)
def generate_report(
    session_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: ReportService = Depends(get_report_service),
) -> ReportRecord:
    try:
        return service.generate_report(user_id, session_id)
    except Exception as exc:
        raise _http_error(exc) from exc


@router.get(
    "/{session_id}/report",
    response_model=ReportRecord,
)
def get_report(
    session_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: ReportService = Depends(get_report_service),
) -> ReportRecord:
    try:
        return service.get_report(user_id, session_id)
    except Exception as exc:
        raise _http_error(exc) from exc


@router.get("/{session_id}", response_model=ExamSessionRecord)
def get_exam(
    session_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: ExamService = Depends(get_exam_service),
) -> ExamSessionRecord:
    try:
        return service.get_exam(user_id, session_id)
    except Exception as exc:
        raise _http_error(exc) from exc


@router.post("/{session_id}/start", response_model=ExamStartResponse)
def start_exam(
    session_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: ExamService = Depends(get_exam_service),
) -> ExamStartResponse:
    try:
        return service.start_exam(user_id, session_id)
    except Exception as exc:
        raise _http_error(exc) from exc


@router.post("/{session_id}/generate-question", response_model=QuestionRecord)
def generate_question(
    session_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: ExamService = Depends(get_exam_service),
) -> QuestionRecord:
    try:
        return service.generate_question(user_id, session_id)
    except Exception as exc:
        raise _http_error(exc) from exc


@router.get("/{session_id}/current-question", response_model=CurrentQuestionResponse)
def get_current_question(
    session_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: ExamService = Depends(get_exam_service),
) -> CurrentQuestionResponse:
    try:
        return service.get_current_question(user_id, session_id)
    except Exception as exc:
        raise _http_error(exc) from exc


@router.post(
    "/{session_id}/questions/{question_id}/answer",
    response_model=AnswerSubmissionResponse,
)
def submit_answer(
    session_id: UUID,
    question_id: UUID,
    request: AnswerSubmissionRequest,
    user_id: UUID = Depends(get_current_user_id),
    service: EvaluationService = Depends(get_evaluation_service),
) -> AnswerSubmissionResponse:
    try:
        normalized = request.normalized()
        answer, evaluation = service.submit_answer(
            user_id=user_id,
            session_id=session_id,
            question_id=question_id,
            answer_text=normalized.answer_text,
        )
        return AnswerSubmissionResponse(answer=answer, evaluation=evaluation)
    except Exception as exc:
        raise _http_error(exc) from exc


@router.post(
    "/{session_id}/chat/turn",
    response_model=ChatTurnResponse,
)
def submit_chat_turn(
    session_id: UUID,
    request: ChatTurnRequest,
    user_id: UUID = Depends(get_current_user_id),
    service: ConversationService = Depends(get_conversation_service),
) -> ChatTurnResponse:
    try:
        normalized = request.normalized()
        return service.submit_turn(
            user_id=user_id,
            session_id=session_id,
            question_id=request.question_id,
            answer_text=normalized.answer_text,
        )
    except Exception as exc:
        raise _http_error(exc) from exc


@router.get(
    "/{session_id}/knowledge-state",
    response_model=list[KnowledgeStateRecord],
)
def get_knowledge_state(
    session_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: KnowledgeStateService = Depends(get_knowledge_service),
) -> list[KnowledgeStateRecord]:
    try:
        return service.list_knowledge_states(user_id, session_id)
    except Exception as exc:
        raise _http_error(exc) from exc


@router.get(
    "/{session_id}/topic-performance",
    response_model=list[TopicPerformanceRecord],
)
def get_topic_performance(
    session_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: KnowledgeStateService = Depends(get_knowledge_service),
) -> list[TopicPerformanceRecord]:
    try:
        return service.list_topic_performance(user_id, session_id)
    except Exception as exc:
        raise _http_error(exc) from exc


@router.post("/{session_id}/complete", response_model=ExamCompletionResponse)
def complete_exam(
    session_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: ExamService = Depends(get_exam_service),
) -> ExamCompletionResponse:
    try:
        return service.complete_exam(user_id, session_id)
    except Exception as exc:
        raise _http_error(exc) from exc
