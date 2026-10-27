-- UT 응답 테이블
create table if not exists public.ut_responses (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  study text not null,
  variant text,
  data jsonb not null
);
create index if not exists ut_responses_study_idx on public.ut_responses (study, id);

alter table public.ut_responses enable row level security;

-- 누구나(링크로 연 참여자) 응답 추가 가능
drop policy if exists "ut insert" on public.ut_responses;
create policy "ut insert" on public.ut_responses
  for insert to anon, authenticated with check (true);

-- 읽기는 결과 화면에서 읽기 토큰을 보낸 경우에만
drop policy if exists "ut read with token" on public.ut_responses;
create policy "ut read with token" on public.ut_responses
  for select to anon, authenticated
  using (current_setting('request.headers', true)::json->>'x-ut-token' = 'ut-R82-8q89rxbzINPgXxOrRb50');

-- 수정·삭제는 아무도 못 함 (대시보드/서비스 키만 가능)
