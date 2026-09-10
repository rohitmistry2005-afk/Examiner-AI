from __future__ import annotations

from collections import defaultdict
from statistics import mean
from uuid import UUID

from app.ai.gemini_client import GeminiClient
from app.db.repositories.factory import get_repositories
from app.schemas.ai import FinalReportContent
from app.schemas.domain import (
    EvaluationRecord,
    KnowledgeStateRecord,
    PerformanceSummary,
    QuestionRecord,
    ReportRecord,
    TopicPerformanceRecord,
)
from app.models.enums import ExamSessionStatus


class ReportService:
    """Build deterministic performance metrics and an AI-written final report."""

    def __init__(self, repositories: dict | None = None, gemini: GeminiClient | None = None):
        self.repositories = repositories or get_repositories()
        self.exams = self.repositories["exams"]
        self.questions = self.repositories["questions"]
        self.answers = self.repositories["answers"]
        self.evaluations = self.repositories["evaluations"]
        self.knowledge = self.repositories["knowledge"]
        self.performance = self.repositories["performance"]
        self.reports = self.repositories["reports"]
        self.gemini = gemini or GeminiClient()

    @staticmethod
    def _round(value: float, digits: int = 2) -> float:
        return round(float(value), digits)

    @staticmethod
    def _dedupe(values: list[str]) -> list[str]:
        seen: set[str] = set()
        output: list[str] = []
        for value in values:
            cleaned = " ".join(str(value).split())
            key = cleaned.casefold()
            if cleaned and key not in seen:
                seen.add(key)
                output.append(cleaned)
        return output

    def _question_evaluations(self, session_id: UUID) -> list[tuple[QuestionRecord, EvaluationRecord]]:
        questions = [QuestionRecord.model_validate(row) for row in self.questions.list_for_session(session_id)]
        question_by_id = {str(q.id): q for q in questions}
        answers = self.answers.list_for_session(session_id)
        answer_ids = [UUID(str(row["id"])) for row in answers]
        if not answer_ids:
            return []
        evaluations = self.evaluations.list_for_answer_ids(answer_ids)
        pairs: list[tuple[QuestionRecord, EvaluationRecord]] = []
        for row in evaluations:
            evaluation = EvaluationRecord.model_validate(row)
            question = question_by_id.get(str(evaluation.question_id))
            if question is not None:
                pairs.append((question, evaluation))
        return pairs

    def build_performance_summary(self, user_id: UUID, session_id: UUID) -> PerformanceSummary:
        session_row = self.exams.get_for_user(session_id, user_id)
        if not session_row:
            raise LookupError("Exam session not found.")

        session_topics = list(session_row.get("topics") or [])
        configured_main = int(session_row.get("question_count", 0))
        question_rows = [QuestionRecord.model_validate(row) for row in self.questions.list_for_session(session_id)]
        main_questions = [q for q in question_rows if not q.is_follow_up]
        follow_ups = [q for q in question_rows if q.is_follow_up]
        pairs = self._question_evaluations(session_id)
        main_pairs = [(q, e) for q, e in pairs if not q.is_follow_up]
        follow_up_pairs = [(q, e) for q, e in pairs if q.is_follow_up]

        def avg(field: str, items: list[tuple[QuestionRecord, EvaluationRecord]]) -> float:
            return self._round(mean(getattr(e, field) for _, e in items) if items else 0.0, 4)

        main_scores = [e.score for _, e in main_pairs]
        overall = self._round(mean(main_scores) if main_scores else 0.0, 2)
        answered_main = len(main_pairs)
        coverage = self._round(answered_main / configured_main if configured_main else 0.0, 4)

        topic_groups: dict[str, list[EvaluationRecord]] = defaultdict(list)
        for question, evaluation in pairs:
            topic_groups[question.topic.casefold()].append(evaluation)

        topic_stats: list[dict] = []
        knowledge_rows = [KnowledgeStateRecord.model_validate(row) for row in self.knowledge.list_for_session(session_id)]
        knowledge_by_topic = {row.topic.casefold(): row for row in knowledge_rows}
        perf_rows = [TopicPerformanceRecord.model_validate(row) for row in self.performance.list_for_session(session_id)]
        perf_by_topic = {row.topic.casefold(): row for row in perf_rows}

        for configured_topic in session_topics:
            key = configured_topic.casefold()
            evals = topic_groups.get(key, [])
            state = knowledge_by_topic.get(key)
            performance = perf_by_topic.get(key)
            topic_scores = [e.score for e in evals]
            topic_stats.append(
                {
                    "topic": configured_topic,
                    "evaluated_answers": len(evals),
                    "average_score": self._round(mean(topic_scores) if topic_scores else (performance.average_score if performance else 0.0), 2),
                    "accuracy": self._round(state.mastery_score if state else (performance.accuracy if performance else 0.0), 4),
                    "mastery_score": self._round(state.mastery_score if state else 0.0, 4),
                    "current_difficulty": state.current_difficulty if state else int(session_row.get("initial_difficulty", 3)),
                }
            )

        strong_topics = [
            item["topic"] for item in topic_stats
            if item["evaluated_answers"] and (item["mastery_score"] >= 0.8 or item["average_score"] >= 8.0)
        ]
        weak_topics = [
            item["topic"] for item in topic_stats
            if item["evaluated_answers"] and (item["mastery_score"] < 0.5 or item["average_score"] < 5.0)
        ]
        misconceptions = self._dedupe(
            [concept for state in knowledge_rows for concept in state.misconceptions]
        )
        concepts_to_revise = self._dedupe(
            [concept for state in knowledge_rows for concept in state.weak_concepts]
        )[:20]

        return PerformanceSummary(
            exam_session_id=session_id,
            overall_score=overall,
            configured_main_questions=configured_main,
            generated_main_questions=len(main_questions),
            answered_main_questions=answered_main,
            follow_up_questions=len(follow_ups),
            evaluated_answers=len(pairs),
            evaluated_follow_up_answers=len(follow_up_pairs),
            topic_coverage=coverage,
            average_correctness=avg("correctness", main_pairs),
            average_completeness=avg("completeness", main_pairs),
            average_conceptual_understanding=avg("conceptual_understanding", main_pairs),
            strong_topics=self._dedupe(strong_topics),
            weak_topics=self._dedupe(weak_topics),
            concepts_to_revise=concepts_to_revise,
            misconceptions=misconceptions[:20],
            topic_breakdown=topic_stats,
        )

    def _build_report_prompt(self, summary: PerformanceSummary) -> str:
        return f"""
You are the senior examiner writing the final performance report for an AI-conducted examination.
Use only the supplied performance evidence. Do not invent scores, topics, or achievements.
The examination was conversational: follow-up questions probe gaps but do not count toward the configured main-question total.
Write concise, professional, student-facing feedback.

Performance evidence:
{summary.model_dump_json(indent=2)}

Return a final report with:
- summary: a concise overall assessment;
- strong_areas: the strongest demonstrated topic/skill areas;
- weak_areas: the most important areas needing improvement;
- concepts_to_revise: concrete concepts from the evidence;
- recommendations: actionable next-study steps;
- closing_feedback: constructive closing examiner feedback.
""".strip()

    def generate_report(self, user_id: UUID, session_id: UUID) -> ReportRecord:
        session_row = self.exams.get_for_user(session_id, user_id)
        if not session_row:
            raise LookupError("Exam session not found.")
        if session_row.get("status") not in {
            ExamSessionStatus.IN_PROGRESS.value,
            ExamSessionStatus.COMPLETED.value,
        }:
            raise ValueError("A final report requires an active or completed exam.")

        existing = self.reports.get_for_session(session_id, user_id)
        if existing:
            return ReportRecord.model_validate(existing)

        summary = self.build_performance_summary(user_id, session_id)
        if summary.answered_main_questions < summary.configured_main_questions:
            raise ValueError(
                "A final report requires an evaluated answer for every configured main question."
            )
        if summary.evaluated_answers == 0:
            raise ValueError("A final report requires at least one evaluated answer.")

        content = self.gemini.generate_structured(self._build_report_prompt(summary), FinalReportContent)
        payload = {
            "exam_session_id": str(session_id),
            "user_id": str(user_id),
            "overall_score": summary.overall_score,
            "summary": content.summary,
            "strong_areas": content.strong_areas,
            "weak_areas": content.weak_areas,
            "concepts_to_revise": content.concepts_to_revise,
            "recommendations": content.recommendations,
            "closing_feedback": content.closing_feedback,
            "performance_snapshot": summary.model_dump(mode="json"),
        }
        row = self.reports.upsert(payload)
        return ReportRecord.model_validate(row)

    def get_report(self, user_id: UUID, session_id: UUID) -> ReportRecord:
        session = self.exams.get_for_user(session_id, user_id)
        if not session:
            raise LookupError("Exam session not found.")
        row = self.reports.get_for_session(session_id, user_id)
        if not row:
            raise LookupError("Final report has not been generated yet.")
        return ReportRecord.model_validate(row)
