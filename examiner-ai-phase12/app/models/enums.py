from enum import StrEnum


class ExamSessionStatus(StrEnum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class ExamMode(StrEnum):
    SEMESTER = "semester"
    VIVA = "viva"
    TECHNICAL_TEST = "technical_test"


class QuestionType(StrEnum):
    CONCEPTUAL = "conceptual"
    TECHNICAL = "technical"
    ANALYTICAL = "analytical"
    PROBLEM_SOLVING = "problem_solving"
    FOLLOW_UP = "follow_up"


class QuestionStatus(StrEnum):
    GENERATED = "generated"
    ASKED = "asked"
    ANSWERED = "answered"
    SKIPPED = "skipped"


class EvaluationDecision(StrEnum):
    NEXT = "next"
    FOLLOW_UP = "follow_up"
    REINFORCE = "reinforce"


class DocumentSourceType(StrEnum):
    SYLLABUS = "syllabus"
    STUDY_MATERIAL = "study_material"
    REFERENCE = "reference"
    OTHER = "other"
