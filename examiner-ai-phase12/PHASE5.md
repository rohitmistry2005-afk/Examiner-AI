# ExaminerAI — Phase 5: Answer Submission + AI Evaluation

Phase 5 implements the free-form answer and evaluation pipeline on top of Phase 4.

## Implemented

- `AnswerSubmissionRequest` and `AnswerSubmissionResponse`
- `AnswerEvaluationResult` structured Gemini schema
- Evaluation prompt builder
- `EvaluationService`
- Answer repository idempotency lookup
- Persist answer
- Evaluate with Gemini
- Persist structured evaluation
- Mark question answered
- Clear current-question pointer
- Reject answers to non-current questions
- Reject answers outside an in-progress exam
- Prevent duplicate evaluation calls on retry

## API

`POST /api/exams/{session_id}/questions/{question_id}/answer`

Request:
```json
{"answer_text": "student's free-form answer"}
```

Response contains the persisted answer and evaluation.

## Phase boundary

Phase 5 evaluates the answer only. Knowledge-state mutation, adaptive decisions, and Socratic follow-up orchestration remain in Phases 6–8.

`evaluations.decision` is stored as `next` as a temporary compatibility value because the Phase 2 database schema requires it; Phase 7/8 will own the actual decision policy.
