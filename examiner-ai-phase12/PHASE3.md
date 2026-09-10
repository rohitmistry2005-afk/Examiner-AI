# ExaminerAI — Phase 3: Examination Domain Engine

Phase 3 implements the deterministic examination lifecycle on top of the Phase 2 persistence layer.

## Included

- Exam creation with normalized/deduplicated topics
- Exam session retrieval and listing
- Explicit session states: `created`, `in_progress`, `completed`, `abandoned`
- Start/complete lifecycle transitions
- Current-question contract
- Main-question count enforcement hook for the configured question limit
- Repository methods for sequence tracking and question state transitions
- API routes under `/api/exams`
- Unit tests for normalization and lifecycle rules

## API

- `POST /api/exams`
- `GET /api/exams`
- `GET /api/exams/{session_id}`
- `POST /api/exams/{session_id}/start`
- `GET /api/exams/{session_id}/current-question`
- `POST /api/exams/{session_id}/complete`

## Design boundary

Phase 3 intentionally does not call Gemini and does not implement RAG, evaluation, adaptation, or reports. Those layers will consume this deterministic examination backbone in later phases.

The current-question endpoint can legitimately return `question: null` immediately after starting an exam because question generation is Phase 4.
