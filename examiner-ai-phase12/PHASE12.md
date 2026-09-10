# ExaminerAI — Phase 12

## Full end-to-end testing and release gates

The permanent product requirement remains:

**ExaminerAI is a chatbot-style AI examiner that conducts the entire examination conversationally.**

Phase 12 is the integration-validation phase. It does not replace the architecture from Phases 1–11. Instead, it verifies that the major layers compose correctly through the public FastAPI API and that important invalid states are rejected safely.

### End-to-end coverage

`tests/test_phase12_end_to_end.py` runs the real FastAPI application with dependency-injected in-memory repositories and deterministic Gemini doubles. This keeps the suite reproducible without requiring live Supabase or Gemini credentials.

The primary scenario exercises this complete path:

```text
Create exam
  → Start exam
  → Generate first conversational question
  → Student answers through /chat/turn
  → Gemini evaluation
  → Knowledge state + topic performance update
  → Adaptive decision
  → Socratic follow-up
  → Student answers follow-up
  → Next main question
  → Student answers final main question
  → Performance summary
  → Final report generation
  → Idempotent report retrieval
  → Exam completion
```

The scenario also verifies that Google Search grounding is invoked through the existing Gemini boundary without adding a separate search provider.

### Integration boundaries tested

- FastAPI routing and response-model serialization
- Authentication dependency override boundary
- Exam creation and lifecycle transitions
- Conversational chat-turn orchestration
- Free-form answer validation
- Gemini structured evaluation boundary
- Knowledge-state persistence behavior
- Topic-performance persistence behavior
- Adaptive topic/difficulty decisions
- Socratic follow-up creation and parent linkage
- Web RAG grounding invocation
- Performance-summary calculation
- Final report generation and persistence
- Final-report idempotency
- Protection against premature report generation
- Protection against answering a non-current question
- Unauthenticated API rejection

### Test strategy

The end-to-end suite is intentionally hermetic:

- repositories are in-memory test doubles;
- Gemini structured generation and grounding are deterministic doubles;
- no live network calls are required;
- production service classes and FastAPI route handlers are exercised unchanged.

Earlier phase unit tests remain part of the regression suite and continue to validate individual components.

An optional live environment can later be added for external-provider smoke tests, but live credentials are not required for the Phase 12 regression gate.

### Commands

Run the full regression suite:

```bash
pytest -q
```

Run only Phase 12 end-to-end tests:

```bash
pytest -m e2e -q
```

Run Python compilation validation:

```bash
python -m compileall app tests
```

### Release gate

Phase 12 is considered passing only when:

1. the complete pytest suite has zero failures;
2. the Phase 12 `e2e` suite passes;
3. all application and test modules compile;
4. the final source package can be installed and imported without test-only runtime services.

### Architecture constraints retained

- chatbot-first examination;
- Python + FastAPI;
- Supabase PostgreSQL + pgvector;
- Gemini API;
- Gemini Google Search grounding;
- document RAG through Supabase pgvector;
- no separate vector database;
- no external search provider;
- no WebSocket;
- no background worker/queue;
- no LangChain/LlamaIndex/LangGraph;
- modular monolith.
