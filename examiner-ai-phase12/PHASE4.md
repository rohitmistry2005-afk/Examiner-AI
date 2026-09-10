# ExaminerAI Backend — Phase 4

## Status

Phase 4 is complete.

## Objective

Connect the deterministic examination engine to Gemini for validated AI question generation.

## Implemented

- Thin `GeminiClient` boundary around `google-genai`.
- Configurable generation model (`GEMINI_GENERATION_MODEL`).
- Structured JSON output validated with Pydantic.
- Question-generation schema with:
  - question text
  - topic
  - difficulty
  - question type
  - expected answer points
- Deterministic topic selection for the current phase (round-robin across configured topics).
- Recent-question context included in the generation prompt to reduce repetition.
- Generated question validation against configured topics and difficulty bounds.
- Persistence of generated questions through the existing repository layer.
- Current-question pointer updated in the exam session.
- Exam start can generate the initial question when the AI service is available.
- Explicit `POST /api/exams/{session_id}/generate-question` endpoint.
- Reuse of an existing current question; duplicate Gemini calls are avoided.

## API additions

```http
POST /api/exams/{session_id}/generate-question
```

The existing start endpoint now optionally returns:

```json
{
  "session": { "...": "..." },
  "question": {
    "id": "...",
    "topic": "...",
    "difficulty": 3,
    "question_text": "...",
    "expected_points": ["...", "...", "..."]
  }
}
```

## Architectural boundary

Gemini does not own examination state. The backend owns session state, topic eligibility, sequence numbers, persistence, and question limits. Gemini supplies the structured question content.

RAG is intentionally not connected yet; document RAG and web grounding remain dedicated later phases.

## Verification

All tests pass locally.
