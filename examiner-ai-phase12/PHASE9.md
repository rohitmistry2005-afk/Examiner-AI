# ExaminerAI — Phase 9

## Document RAG for the Chatbot Examiner

The permanent product requirement remains:

**ExaminerAI is a chatbot-style AI examiner that conducts the entire examination conversationally.**

Phase 9 grounds that conversation in user-provided PDF/DOCX academic documents.

### Ingestion

```text
PDF/DOCX upload
    ↓
Text extraction
    ↓
Page-aware chunking
    ↓
Gemini Embedding 2
    ↓
Supabase pgvector
```

### Retrieval

```text
Examiner query
    ↓
Gemini Embedding 2
    ↓
Supabase match_document_chunks()
    ↓
Top relevant document chunks
    ↓
Prompt context
    ↓
Gemini
```

### Grounded examiner operations

Retrieved document context is now available to:
- question generation;
- answer evaluation;
- Socratic follow-up generation.

The user’s configured subject is used as a retrieval filter.

### Supported uploads

- PDF
- DOCX
- 10 MB maximum

No OCR engine, separate vector database, LangChain, LlamaIndex, or external document service is introduced.

### API

`POST /api/documents`

Multipart fields:
- `file`
- `subject` (optional)
- `source_type`: `syllabus | study_material | reference | other`

### Scope

Phase 9 is document RAG only. Web grounding remains Phase 10.
