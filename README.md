# Store Insight Lab

매장 현장 검증 데이터를 모으는 도구 모음. GitHub Pages로 서비스하고, 응답은 Supabase(`Store Insight Lab` 프로젝트)에 저장해요.

- 홈: `https://minsunkim1-dot.github.io/store-insight-lab/`
- UT Lab: `https://minsunkim1-dot.github.io/store-insight-lab/ut-lab/?study=<study id>`

## ut-lab
- `ut-lab/index.html` — 참여자·관리자 페이지 (한 파일)
- `ut-lab/studies/<id>.json` — UT 설정(시안·화면·질문). 페이지가 `?study=<id>`로 읽어요
- `ut-lab/assets/` — 이미지·폰트·모션
- 관리자(결과) 화면: `…/ut-lab/?study=<id>&admin=<읽기 토큰>` 으로 한 번 열면 그 브라우저에 기억돼요
- 응답 테이블: Supabase `ut_responses` (study, variant, data jsonb). 추가는 누구나, 읽기는 `x-ut-token` 헤더로만 (`supabase/setup.sql`)

## 새 UT 추가
1. `ut-lab/studies/<새 id>.json` 추가 (Claude에게 "새 UT 세팅해줘")
2. 링크 `…/ut-lab/?study=<새 id>` 배포
3. 결과는 `&admin=<토큰>`으로 열거나 Claude에게 "결과 요약해줘"

## 캔버스 → UT 동기화
`tools/ut-sync/` — Claude Design 캔버스 보드를 UT 화면으로 옮기는 도구. "캔버스 반영해줘"라고 하면 Claude가 실행하고 `studies/*.json`을 갱신해 푸시해요.
