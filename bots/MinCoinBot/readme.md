# MinCoinBot

## 개요
업비트 멀티 종목(BTC, ETH, XRP, SOL 등) 가격을 조회하여 듀얼 타임프레임(매도: 1분봉, 매수: 5분봉) 기반으로 자동 매매 판단을 수행하는 **가상 매매 시뮬레이션 봇**.
실제 업비트 주문을 넣지 않으며, 로컬 가상 자금(state.json)으로 시뮬레이션한다.
config.json의 symbols 배열에 종목을 나열하면 전부 순회하며 매매한다.

## 터미널 명령어
```
python3 /Users/chulyong/Documents/RecentProjects/Argos/bots/MinCoinBot/MinCoinBotStarter.py

python3 /Users/doil/Documents/RecentProjects/Argos/bots/MinCoinBot/MinCoinBotStarter.py

```

## 매매 로직

### 기본 설정 (config.json)
| 항목 | 기본값 | 비고 |
|------|--------|------|
| 종목 | BTC, ETH, XRP, SOL | symbols 배열로 관리 |
| 매도 체크 간격 | 1분봉 | 빠른 익절 포착용 |
| 매수 체크 간격 | 5분봉 | 하락 시 투입 속도 제한 |
| 매수 금액 | 5,000원 | 봉당 매수 단위 (종목당) |
| 익절 기준 | +1.5% | 평단 대비 수익률 |
| 손절 기준 | 없음 | 평단 낮추기로 대응 |
| 매수 수수료 | 0.05% | 업비트 실제 수수료 기준 |
| 매도 수수료 | 0.05% | 업비트 실제 수수료 기준 |

### 흐름 (종목별 독립 실행)
1. **첫 번째 봉** → 무조건 5,000원어치 매수
2. **두 번째 봉부터** 매 1분마다:
   - 수익률 ≥ +1.5% → 즉시 전량 익절(시장가 매도) → 1번으로
3. **매 5분마다** 매수 판단:
   - 직전 5분봉이 음봉 AND 현재가 < 평단 → 5,000원 추가 매수
   - 그 외 → 대기
4. 매도 후 다시 1번부터 반복

※ 잔고(balance)는 전 종목 공유. 한 종목에서 매수하면 다른 종목 매수 가능 금액이 줄어듦.

## 가상 자금 (state.json)
| 항목 | 초기값 | 설명 |
|------|--------|------|
| balance | 10,000,000원 | 사용 가능 잔고 (전 종목 공유) |
| total_realized_profit | 0 | 누적 실현 손익 |
| symbols.{종목}.holding_qty | 0.0 | 보유 수량 |
| symbols.{종목}.holding_avg_price | 0.0 | 평균 매수 단가 |
| symbols.{종목}.total_buy_amount | 0.0 | 총 매수 금액(원화) |
| symbols.{종목}.is_first_candle | true | 첫 봉 여부 |

매수 시 balance에서 차감, 매도 시 balance에 가산. 수수료는 각각 적용.

## 구글시트 기록
환경변수 `GOOGLE_SHEET_NAME_4` (기본값: 민코인봇) 시트에 기록.
컬럼: 날짜 / 시간 / 종목 / 현재가 / 매수액 / 매도액 / 총평가액 / 현금 / 투자금액 / 수익률 / 종목평가금 / 순이익

## 파일 구조
```
MinCoinBot/
├── MinCoinBotStarter.py   # 봇 실행 진입점
├── Reset.py               # state 초기화 (config의 symbols 기반)
├── config.json            # 설정 변수 (종목 목록 포함)
├── state.json             # 가상 자금 상태 (런타임 중 갱신)
└── readme.md
```