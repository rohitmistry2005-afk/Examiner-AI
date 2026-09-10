from uuid import UUID

from app.models.enums import ExamSessionStatus, QuestionStatus
from app.schemas.domain import (
    CurrentQuestionResponse,
    ExamCompletionResponse,
    ExamCreateRequest,
    ExamSessionRecord,
    ExamStartResponse,
    QuestionRecord,
)
from app.db.repositories.factory import get_repositories
from app.services.question_service import QuestionService
from app.services.report_service import ReportService


class ExamService:
    def __init__(self, repositories: dict | None = None, question_service: QuestionService | None = None, report_service: ReportService | None = None):
        self.repositories = repositories or get_repositories()
        self.exams = self.repositories["exams"]
        self.questions = self.repositories["questions"]
        self.question_service = question_service
        self.report_service = report_service

    def create_exam(self, user_id: UUID, request: ExamCreateRequest) -> ExamSessionRecord:
        normalized = request.normalized()
        row = self.exams.create(
            {
                "user_id": str(user_id),
                "subject": normalized.subject,
                "topics": normalized.topics,
                "exam_mode": normalized.exam_mode.value,
                "initial_difficulty": normalized.difficulty,
                "question_count": normalized.question_count,
                "status": ExamSessionStatus.CREATED.value,
            }
        )
        return ExamSessionRecord.model_validate(row)

    def get_exam(self, user_id: UUID, session_id: UUID) -> ExamSessionRecord:
        row = self.exams.get_for_user(session_id, user_id)
        if not row:
            raise LookupError("Exam session not found.")
        return ExamSessionRecord.model_validate(row)

    def list_exams(self, user_id: UUID) -> list[ExamSessionRecord]:
        return [
            ExamSessionRecord.model_validate(row)
            for row in self.exams.list_for_user(user_id)
        ]

    def start_exam(self, user_id: UUID, session_id: UUID) -> ExamStartResponse:
        session = self.get_exam(user_id, session_id)
        if session.status == ExamSessionStatus.COMPLETED:
            raise ValueError("A completed exam cannot be started again.")
        if session.status == ExamSessionStatus.ABANDONED:
            raise ValueError("An abandoned exam cannot be restarted.")
        if session.status == ExamSessionStatus.IN_PROGRESS:
            if self.question_service is not None and not self.questions.get_current(session_id):
                question = self.question_service.generate_next_main_question(user_id, session_id)
                return ExamStartResponse(session=self.get_exam(user_id, session_id), question=question)
            return ExamStartResponse(session=session)

        updated = self.exams.start(session_id, user_id)
        response = ExamStartResponse(session=ExamSessionRecord.model_validate(updated))

        if self.question_service is not None:
            question = self.question_service.generate_next_main_question(user_id, session_id)
            response = ExamStartResponse(
                session=ExamSessionRecord.model_validate(
                    self.exams.get_for_user(session_id, user_id)
                ),
                question=question,
            )
        return response

    def generate_question(self, user_id: UUID, session_id: UUID) -> QuestionRecord:
        if self.question_service is None:
            self.question_service = QuestionService(self.repositories)
        return self.question_service.generate_next_main_question(user_id, session_id)

    def complete_exam(self, user_id: UUID, session_id: UUID) -> ExamCompletionResponse:
        session = self.get_exam(user_id, session_id)
        if session.status == ExamSessionStatus.CREATED:
            raise ValueError("An exam must be started before it can be completed.")
        if session.status == ExamSessionStatus.COMPLETED:
            return ExamCompletionResponse(session=session)
        if session.status == ExamSessionStatus.ABANDONED:
            raise ValueError("An abandoned exam cannot be completed.")

        # Phase 11: generate the immutable final report before marking the session
        # complete. Earlier lightweight service tests do not inject a report service,
        # so their lifecycle behavior remains unchanged.
        if self.report_service is not None:
            self.report_service.generate_report(user_id, session_id)

        updated = self.exams.complete(session_id, user_id)
        return ExamCompletionResponse(session=ExamSessionRecord.model_validate(updated))

    def get_current_question(
        self, user_id: UUID, session_id: UUID
    ) -> CurrentQuestionResponse:
        session = self.get_exam(user_id, session_id)
        if session.status == ExamSessionStatus.COMPLETED:
            return CurrentQuestionResponse(question=None, exam_completed=True)
        if session.status != ExamSessionStatus.IN_PROGRESS:
            raise ValueError("Exam must be in progress to fetch the current question.")

        question = self.questions.get_current(session_id)
        if not question:
            return CurrentQuestionResponse(question=None, exam_completed=False)
        return CurrentQuestionResponse(
            question=QuestionRecord.model_validate(question),
            exam_completed=False,
        )

    def validate_question_addition(
        self, user_id: UUID, session_id: UUID, is_follow_up: bool
    ) -> ExamSessionRecord:
        session = self.get_exam(user_id, session_id)
        if session.status != ExamSessionStatus.IN_PROGRESS:
            raise ValueError("Questions can only be added to an in-progress exam.")
        if not is_follow_up and self.exams.count_questions(session_id) >= session.question_count:
            raise ValueError("The configured question limit has been reached.")
        return session
