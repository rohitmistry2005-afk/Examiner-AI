# ExaminerAI — Backend Phase 11

Phase 12 contains the complete ExaminerAI backend through end-to-end integration validation.

## Run

```bash
python -m venv .venv
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Tests

Run from this directory:

```bash
pytest -q
```

## Included through Phase 11

- FastAPI foundation
- Supabase database migration + pgvector
- Repository layer
- Exam creation/list/retrieval
- Exam start/complete lifecycle
- Current-question contract
- Topic normalization
- Question-limit enforcement hook
- Authentication dependency boundary

## Not yet included

- Gemini question generation
- Answer evaluation
- Knowledge-state updates
- Adaptive engine
- Follow-up generation
- Document ingestion/RAG ✅
- Web RAG ✅ (Phase 10)
- Final reports ✅ (Phase 11)
- WebSockets
- Deployment


## Phase 12 end-to-end testing

Phase 12 adds a hermetic full-examination API scenario and release-quality regression gates.
See `PHASE12.md`.

Run:

```bash
pytest -q
pytest -m e2e -q
python -m compileall app tests
```

## Development status

- Phase 1: Foundation ✅
- Phase 2: Supabase schema/repositories ✅
- Phase 3: Examination domain engine ✅
- Phase 4: Gemini question generation ✅
- Phase 11: Performance analytics + final report ✅
- Phase 12: Full end-to-end testing ✅


## Phase 5
Free-form answer submission and structured Gemini answer evaluation are implemented. See `PHASE5.md`.


## Phase 6
See `PHASE6.md` for the persistent student knowledge-state and topic-performance layer.


## Phase 8
See `PHASE8.md` for Socratic follow-up conversation behavior.
