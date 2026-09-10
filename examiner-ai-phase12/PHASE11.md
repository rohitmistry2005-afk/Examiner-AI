# ExaminerAI — Phase 11

## Performance analytics + final report

The permanent product requirement remains:

**ExaminerAI is a chatbot-style AI examiner that conducts the entire examination conversationally.**

Phase 11 adds the performance/report layer without changing the conversational examination loop.
The existing stored evaluations, knowledge state, topic performance, and question graph are used as
source evidence for the final result.

### Performance summary

`ReportService` deterministically computes:

- overall score from configured main-question evaluations;
- configured/generated/answered main-question counts;
- follow-up question counts;
- answer-quality averages for correctness, completeness, and conceptual understanding;
- syllabus topic coverage;
- strong and weak topics;
- concepts to revise and recorded misconceptions;
- topic-level score, accuracy, mastery, and difficulty snapshot.

Follow-up probes are included as evidence and reported separately, but they do **not** inflate the
configured main-question total or the main-question overall score.

### Final report generation

`GeminiClient.generate_structured()` generates student-facing report language from the deterministic
performance evidence. The structured content is persisted to the existing `reports` table, together
with a `performance_snapshot` JSON document so the frontend can render charts/details without
recomputing analytics.

### API

```text
GET  /api/exams/{session_id}/performance-summary
POST /api/exams/{session_id}/report
GET  /api/exams/{session_id}/report
POST /api/exams/{session_id}/complete
```

The completion path now generates the final report before transitioning the exam to `completed` when
the production `ReportService` is configured. Report generation is idempotent: an existing report is
returned rather than regenerated.

### Database change

`supabase/migrations/002_phase11_report_snapshot.sql` adds:

```sql
reports.performance_snapshot jsonb not null default '{}'
```

The original report columns remain the canonical student-facing report content.

### Design constraints

- preserves chatbot-first examination behavior;
- no new vector database;
- no new search provider;
- no WebSocket;
- no background worker/queue;
- no LangChain/LlamaIndex/LangGraph;
- analytics are deterministic and reproducible from persisted examination evidence.
