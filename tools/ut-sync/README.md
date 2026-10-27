# 캔버스 → UT 화면 동기화

- 원본: 결제수단별 혜택 와이어프레임 캔버스 (https://claude.ai/artifact/EnfY5dE6aUfQngLp1rQcXx)
- 대상: 결제 수단 혜택 UT (https://claude.ai/artifact/Hy2hZkWpRrb3eD73cgUvjh), DB 문서 `config/study`

## 쓰는 법 (Claude에게 "캔버스 반영해줘")
1. 캔버스에서 map.json의 보드 파일(`project/<board>.dc.html`)을 읽어 `boards/`에 저장
2. UT의 `config/study`를 읽어 저장
3. `python3 sync.py boards <읽은 config> <out.json>` 실행 → 화면별 결과 보고
4. 바뀐 화면을 확인(렌더·클릭 흐름)한 뒤 `config/study`에 out.json을 버전 고정해서 저장

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
