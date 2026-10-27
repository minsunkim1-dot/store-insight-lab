# 캔버스 → UT 화면 동기화

- 원본: 결제수단별 혜택 와이어프레임 캔버스 (https://claude.ai/artifact/EnfY5dE6aUfQngLp1rQcXx)
- 대상: GitHub Pages UT (`ut-lab/studies/selfpos-benefit.json`) — 예전 claude.ai UT(DB `config/study`)는 더 이상 갱신하지 않음

## 쓰는 법 (Claude에게 "캔버스 반영해줘")
1. 캔버스에서 map.json의 보드 파일(`project/<board>.dc.html`)을 읽어 `boards/`에 저장
2. `python3 sync.py boards ../../ut-lab/studies/selfpos-benefit.json out.json` 실행 → 화면별 결과 보고
3. 바뀐 화면을 확인(렌더·클릭 흐름)한 뒤 out.json을 `ut-lab/studies/selfpos-benefit.json`에 덮어쓰고 git push (Pages 재배포 1~2분)

## 연결된 화면
| 캔버스 보드 | UT 화면 |
|---|---|
| Self_Method | a-method, b-method |
| M1_SelfPopup_Plcc_Flat | a-list (A 목록형) |
| Idea7_SelfWideCard_Label | b-wide (B 와이드 카드형) |
| Self_EasyPay | a-easy, b-easy |
| Self_Guide_CardPlcc / CardLink | *-card-ms / *-card-link |
| Self_Guide_Payco / Kakao | *-scan-payco / *-scan-kakao |
| Self_CompleteDialog | *-paid |

연결 안 된 화면(Figma 원본): 할부 선택, 기본 카드·태그·스캔, 결제 완료, 삼성카드 ⓘ 안내.

## UT에서 유지하는 차이 (map.json)
- 금액: 4개 · 196,210원, 최대 10,000원 할인, 예상 적립 3,920원, 페이코 -9,810원
- 무신사 현대카드 행 제거(미보유), 카카오페이 첫 결제(-10,000원)를 페이코 앞에 정렬
- B안: "예상 적립금" 라벨, "10% ⓘ" 줄바꿈 묶음
- 전체: "결제 혜택" → "결제혜택"
- 누르는 영역(data-hs), 모션(lottie), 결제 금액 표시(data-amount)는 UT 것 유지
- 캔버스 이미지 id → UT 이미지 id 표(blobs). 표에 없는 이미지가 나오면 그 화면은 그대로 두고 "복사할 이미지"로 알려줌

- 이미지 경로: map.json의 `assets_dir`로 `/_blob/<id>` → `assets/<id>.<ext>` 변환
- 스팟 지정: `text`(글자로 찾기) / `svg_in`(글자 요소 안의 svg 아이콘 감싸기) / `css`+`nth`(선택자)
- `labels`: 보드 반영 시 함께 바꿀 결제수단 라벨
