alter table public.reports
    add column if not exists performance_snapshot jsonb not null default '{}'::jsonb;
