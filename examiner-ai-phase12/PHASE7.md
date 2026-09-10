# ExaminerAI — Phase 7

## Adaptive + Chatbot Conversation Engine

Phase 7 preserves the Phase 1–6 implementation and adds:
1. a deterministic adaptive controller;
2. an explicit chatbot-style examination turn.

### Adaptive controller

```text
Knowledge State
+
Topic Performance
+
Syllabus Coverage
+
Current Difficulty
        ↓
AdaptiveEngine
        ↓
target topic + difficulty + action
```

Rules:
- Uncovered configured topics are prioritized first.
- Mastery < 0.35 decreases difficulty.
- Mastery 0.35–<0.80 maintains difficulty.
- Mastery >= 0.80 increases difficulty.
- Difficulty is always bounded to 1..5.

Gemini generates question language/content; the backend owns the adaptive policy.

### Chatbot boundary

`POST /api/exams/{session_id}/chat/turn`

```text
Student answer
   ↓
Answer evaluation
   ↓
Knowledge-state update
   ↓
Adaptive decision
   ↓
Next question generation
   ↓
Examiner message
```

The response contains the conversational examiner message plus structured evaluation,
adaptive decision, and next question data.

Phase 8 will add targeted Socratic follow-up decisions and parent-child follow-up chains.
