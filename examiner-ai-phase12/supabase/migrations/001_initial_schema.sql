create extension if not exists vector with schema extensions;
create extension if not exists pgcrypto;

create table if not exists public.health_check (
    id smallint primary key default 1,
    created_at timestamptz not null default now()
);

insert into public.health_check (id)
values (1)
on conflict (id) do nothing;

create table if not exists public.exam_sessions (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    subject text not null check (char_length(trim(subject)) > 0),
    topics jsonb not null default '[]'::jsonb,
    exam_mode text not null check (exam_mode in ('semester', 'viva', 'technical_test')),
    initial_difficulty smallint not null check (initial_difficulty between 1 and 5),
    question_count integer not null check (question_count between 1 and 100),
    status text not null default 'created' check (status in ('created', 'in_progress', 'completed', 'abandoned')),
    current_question_id uuid null,
    started_at timestamptz null,
    completed_at timestamptz null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.questions (
    id uuid primary key default gen_random_uuid(),
    exam_session_id uuid not null references public.exam_sessions(id) on delete cascade,
    parent_question_id uuid null references public.questions(id) on delete set null,
    topic text not null,
    difficulty smallint not null check (difficulty between 1 and 5),
    question_type text not null check (question_type in ('conceptual', 'technical', 'analytical', 'problem_solving', 'follow_up')),
    question_text text not null check (char_length(trim(question_text)) > 0),
    expected_points jsonb not null default '[]'::jsonb,
    status text not null default 'generated' check (status in ('generated', 'asked', 'answered', 'skipped')),
    sequence_number integer not null check (sequence_number >= 1),
    is_follow_up boolean not null default false,
    created_at timestamptz not null default now(),
    answered_at timestamptz null,
    unique (exam_session_id, sequence_number)
);

alter table public.exam_sessions
    drop constraint if exists exam_sessions_current_question_fk;

alter table public.exam_sessions
    add constraint exam_sessions_current_question_fk
    foreign key (current_question_id)
    references public.questions(id)
    on delete set null;

create table if not exists public.answers (
    id uuid primary key default gen_random_uuid(),
    question_id uuid not null references public.questions(id) on delete cascade,
    exam_session_id uuid not null references public.exam_sessions(id) on delete cascade,
    user_id uuid not null references auth.users(id) on delete cascade,
    answer_text text not null check (char_length(trim(answer_text)) > 0),
    submitted_at timestamptz not null default now(),
    unique (question_id, user_id)
);

create table if not exists public.evaluations (
    id uuid primary key default gen_random_uuid(),
    answer_id uuid not null unique references public.answers(id) on delete cascade,
    question_id uuid not null references public.questions(id) on delete cascade,
    score numeric(4,2) not null check (score between 0 and 10),
    correctness numeric(5,4) not null check (correctness between 0 and 1),
    completeness numeric(5,4) not null check (completeness between 0 and 1),
    conceptual_understanding numeric(5,4) not null check (conceptual_understanding between 0 and 1),
    strengths jsonb not null default '[]'::jsonb,
    missing_concepts jsonb not null default '[]'::jsonb,
    misconceptions jsonb not null default '[]'::jsonb,
    feedback text not null,
    decision text not null check (decision in ('next', 'follow_up', 'reinforce')),
    created_at timestamptz not null default now()
);

create table if not exists public.knowledge_states (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    exam_session_id uuid not null references public.exam_sessions(id) on delete cascade,
    topic text not null,
    mastery_score numeric(5,4) not null default 0 check (mastery_score between 0 and 1),
    current_difficulty smallint not null default 1 check (current_difficulty between 1 and 5),
    strong_concepts jsonb not null default '[]'::jsonb,
    weak_concepts jsonb not null default '[]'::jsonb,
    misconceptions jsonb not null default '[]'::jsonb,
    attempts integer not null default 0 check (attempts >= 0),
    updated_at timestamptz not null default now(),
    unique (exam_session_id, topic)
);

create table if not exists public.topic_performance (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    exam_session_id uuid not null references public.exam_sessions(id) on delete cascade,
    topic text not null,
    questions_attempted integer not null default 0 check (questions_attempted >= 0),
    average_score numeric(5,2) not null default 0 check (average_score between 0 and 10),
    accuracy numeric(5,4) not null default 0 check (accuracy between 0 and 1),
    updated_at timestamptz not null default now(),
    unique (exam_session_id, topic)
);

create table if not exists public.documents (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    subject text null,
    filename text not null,
    mime_type text not null,
    source_type text not null check (source_type in ('syllabus', 'study_material', 'reference', 'other')),
    storage_path text null,
    status text not null default 'uploaded',
    created_at timestamptz not null default now()
);

create table if not exists public.document_chunks (
    id uuid primary key default gen_random_uuid(),
    document_id uuid not null references public.documents(id) on delete cascade,
    user_id uuid not null references auth.users(id) on delete cascade,
    content text not null,
    page_number integer null check (page_number is null or page_number >= 1),
    chunk_index integer not null check (chunk_index >= 0),
    embedding extensions.vector(768) not null,
    created_at timestamptz not null default now(),
    unique (document_id, chunk_index)
);

create table if not exists public.reports (
    id uuid primary key default gen_random_uuid(),
    exam_session_id uuid not null unique references public.exam_sessions(id) on delete cascade,
    user_id uuid not null references auth.users(id) on delete cascade,
    overall_score numeric(5,2) not null check (overall_score between 0 and 10),
    summary text not null,
    strong_areas jsonb not null default '[]'::jsonb,
    weak_areas jsonb not null default '[]'::jsonb,
    concepts_to_revise jsonb not null default '[]'::jsonb,
    recommendations jsonb not null default '[]'::jsonb,
    closing_feedback text not null,
    created_at timestamptz not null default now()
);

create index if not exists idx_exam_sessions_user_created on public.exam_sessions(user_id, created_at desc);
create index if not exists idx_questions_session_sequence on public.questions(exam_session_id, sequence_number);
create index if not exists idx_answers_session_submitted on public.answers(exam_session_id, submitted_at);
create index if not exists idx_evaluations_question on public.evaluations(question_id);
create index if not exists idx_knowledge_states_session_topic on public.knowledge_states(exam_session_id, topic);
create index if not exists idx_topic_performance_session_topic on public.topic_performance(exam_session_id, topic);
create index if not exists idx_documents_user_created on public.documents(user_id, created_at desc);

create index if not exists idx_document_chunks_embedding_hnsw
on public.document_chunks
using hnsw (embedding extensions.vector_cosine_ops);

create index if not exists idx_document_chunks_document
on public.document_chunks(document_id, chunk_index);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists trg_exam_sessions_updated_at on public.exam_sessions;
create trigger trg_exam_sessions_updated_at
before update on public.exam_sessions
for each row execute function public.set_updated_at();

drop trigger if exists trg_knowledge_states_updated_at on public.knowledge_states;
create trigger trg_knowledge_states_updated_at
before update on public.knowledge_states
for each row execute function public.set_updated_at();

drop trigger if exists trg_topic_performance_updated_at on public.topic_performance;
create trigger trg_topic_performance_updated_at
before update on public.topic_performance
for each row execute function public.set_updated_at();

create or replace function public.match_document_chunks(
    query_embedding extensions.vector(768),
    match_threshold float,
    match_count int,
    filter_user_id uuid,
    filter_document_id uuid default null,
    filter_subject text default null
)
returns table (
    id uuid,
    document_id uuid,
    content text,
    page_number int,
    chunk_index int,
    similarity float
)
language sql
stable
as $$
    select
        dc.id,
        dc.document_id,
        dc.content,
        dc.page_number,
        dc.chunk_index,
        1 - (dc.embedding <=> query_embedding) as similarity
    from public.document_chunks dc
    join public.documents d on d.id = dc.document_id
    where dc.user_id = filter_user_id
      and (filter_document_id is null or dc.document_id = filter_document_id)
      and (filter_subject is null or d.subject = filter_subject)
      and 1 - (dc.embedding <=> query_embedding) >= match_threshold
    order by dc.embedding <=> query_embedding
    limit match_count;
$$;

alter table public.health_check enable row level security;
alter table public.exam_sessions enable row level security;
alter table public.questions enable row level security;
alter table public.answers enable row level security;
alter table public.evaluations enable row level security;
alter table public.knowledge_states enable row level security;
alter table public.topic_performance enable row level security;
alter table public.documents enable row level security;
alter table public.document_chunks enable row level security;
alter table public.reports enable row level security;

create policy "users can read own exam sessions" on public.exam_sessions
for select to authenticated using (auth.uid() = user_id);
create policy "users can create own exam sessions" on public.exam_sessions
for insert to authenticated with check (auth.uid() = user_id);
create policy "users can update own exam sessions" on public.exam_sessions
for update to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "users can access questions in own sessions" on public.questions
for all to authenticated using (
    exists (
        select 1 from public.exam_sessions es
        where es.id = exam_session_id and es.user_id = auth.uid()
    )
) with check (
    exists (
        select 1 from public.exam_sessions es
        where es.id = exam_session_id and es.user_id = auth.uid()
    )
);

create policy "users can access own answers" on public.answers
for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "users can read evaluations for own answers" on public.evaluations
for select to authenticated using (
    exists (
        select 1 from public.answers a
        where a.id = answer_id and a.user_id = auth.uid()
    )
);

create policy "users can access own knowledge states" on public.knowledge_states
for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "users can access own topic performance" on public.topic_performance
for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "users can access own documents" on public.documents
for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "users can access own document chunks" on public.document_chunks
for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "users can access own reports" on public.reports
for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);
