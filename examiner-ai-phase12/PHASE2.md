# ExaminerAI — Phase 2: Supabase Database & Repository Layer

Phase 2 establishes the persistent data model required by the examination engine and RAG system.

## Included

- Supabase PostgreSQL schema migration
- pgvector extension and 768-dimensional document embeddings
- HNSW index for document chunk similarity search
- `match_document_chunks` SQL retrieval function
- Row Level Security policies for user-owned data
- Exam sessions, questions, answers, evaluations
- Per-session knowledge states and topic performance
- Documents, document chunks, and reports
- Parent-child questions for bounded follow-up/Socratic questioning
- Typed Python domain schemas and enums
- Supabase repository abstractions

## Migration

Apply:

`supabase/migrations/001_initial_schema.sql`

against the target Supabase project using the Supabase SQL Editor or Supabase CLI migration workflow.

The local test suite does **not** claim that this SQL has been applied to your Supabase project; no project credentials were supplied during Phase 2.

## Repository design

All database access for domain operations goes through repository classes under `app/db/repositories/`.

The `DocumentRepository.match_chunks()` method calls the Postgres function `match_document_chunks`, keeping vector retrieval in Supabase rather than introducing another vector database.

## Verification

Local verification completed:

- Python compilation: passed
- Phase 2 model tests: passed
- Full available local test suite at this phase: 4 passed
