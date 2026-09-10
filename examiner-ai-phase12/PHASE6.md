# ExaminerAI — Phase 6

## Student Knowledge State

Phase 6 converts validated answer evaluations into persistent, topic-level evidence.

### Implemented

- Topic mastery score
- Running attempts count
- Strong concepts
- Weak concepts
- Persistent misconceptions
- Topic average score
- Topic accuracy
- Bounded current difficulty estimate
- Knowledge-state API
- Topic-performance API
- Automatic update after each successful evaluation

### Flow

```text
Validated Evaluation
        ↓
KnowledgeStateService
        ├── Evidence calculation
        ├── Running mastery update
        ├── Concept evidence merge
        └── Topic performance update
        ↓
Supabase
 ├── knowledge_states
 └── topic_performance
```

### Mastery evidence

The phase derives one bounded evidence value from the evaluator's semantic dimensions:

- correctness: 45%
- completeness: 30%
- conceptual understanding: 25%

The stored mastery score is a running average of this evidence across attempts.

### Scope boundary

Phase 6 stores the student's current knowledge state. It does **not** own the next-question policy.

Phase 7 will use this state to decide:

- next topic
- next difficulty
- reinforce vs advance
- whether a follow-up is required
