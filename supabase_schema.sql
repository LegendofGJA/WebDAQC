-- Jalankan di Supabase SQL Editor (project kamu) sekali saja.

create table if not exists audit_drafts (
  id uuid primary key default gen_random_uuid(),
  store_name text not null,
  audit_date text not null,
  date2 text,
  auditor text,
  pic_on_duty text,
  remarks jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (store_name, audit_date)
);

-- Karena aplikasi tanpa login, RLS dibuka publik (siapapun yang punya
-- SUPABASE_URL + anon key bisa baca/tulis). Cukup untuk tool internal,
-- tapi JANGAN pakai pola ini untuk data sensitif / publik luas.
alter table audit_drafts enable row level security;

create policy "public read" on audit_drafts
  for select using (true);

create policy "public insert" on audit_drafts
  for insert with check (true);

create policy "public update" on audit_drafts
  for update using (true);

create policy "public delete" on audit_drafts
  for delete using (true);
