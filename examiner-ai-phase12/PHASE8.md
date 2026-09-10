# ExaminerAI — Phase 8

## Socratic Follow-up Conversation

**Permanent product constraint:** ExaminerAI is a chatbot-style AI examiner that conducts the
entire examination conversationally.

Phase 8 adds the examiner's Socratic probing behavior on top of Phases 1–7.

### Trigger

A follow-up is considered when evaluation evidence shows:
- a misconception;
- missing concepts;
- score below 6/10;
- completeness below 0.60; or
- conceptual understanding below 0.60.

### Conversation

```text
Student answer
   ↓
Semantic evaluation
   ↓
Knowledge-state update
   ↓
FollowUpService
   ↓
Targeted Socratic examiner question
   ↓
Student answers again
   ↓
Evaluation
```

A maximum of **2 follow-ups per original question** prevents an endless conversation.

Follow-ups use the existing `questions` table with `parent_question_id`, so no new table is required.

### Chat endpoint

`POST /api/exams/{session_id}/chat/turn` now prefers a targeted follow-up when the student's
answer demonstrates a gap. Otherwise it advances to the adaptive next question.

The response contains:
- conversational `examiner_message`;
- evaluation;
- adaptive decision;
- next question/follow-up;
- completion status.

Phase 9 will implement document RAG while preserving this chatbot examiner behavior.
