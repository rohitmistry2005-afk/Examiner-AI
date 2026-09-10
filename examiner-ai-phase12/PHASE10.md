# ExaminerAI — Phase 10

## Web RAG with Gemini Google Search grounding

The permanent product requirement remains:

**ExaminerAI is a chatbot-style AI examiner that conducts the entire examination conversationally.**

Phase 10 adds web retrieval without introducing a separate search provider.
Gemini's managed `google_search` tool is used behind a small `WebRAGService` boundary.

### Architecture

```text
Examiner operation
      ↓
WebRAGService
      ↓
GeminiClient.generate_grounded_text()
      ↓
Gemini + Google Search grounding
      ↓
Grounded factual context + source URLs
      ↓
Existing structured Gemini examiner operation
```

### Where web grounding is used

- main examination question generation;
- semantic answer evaluation;
- Socratic follow-up generation.

The existing document RAG path remains intact. Document context is preserved and
web context is appended when the Google-grounded response is non-empty.

### Source extraction

`GeminiClient` extracts grounded web sources from the Gemini response metadata,
with an annotation-compatible fallback for SDK response variants. A maximum of
8 source URLs is retained for the grounded context.

### Configuration

```env
WEB_RAG_ENABLED=true
```

Set this to `false` to disable web grounding without changing the rest of the
exam engine.

### Design constraints

- no external search API/provider;
- no separate web crawler;
- no separate vector database;
- no LangChain/LlamaIndex/LangGraph;
- no WebSocket;
- existing chatbot examination flow remains unchanged.
