# 📈 SangddaBot (상따봇) - 코스닥 상한가 추적 봇

## 🎯 개요

**상따봇**은 매일 코스닥 시장에서 상한가(+30%)를 기록한 종목들을 찾아 Slack으로 알려주는 자동화 봇입니다.

- **이름 유래**: 상한가 따라가기 → 상따
- **목적**: 당일 상한가 종목 모니터링 및 알림
- **타겟 시장**: KOSDAQ (코스닥) 전 종목

## 📌 상한가의 정의

### 한국 주식시장 상한가 규정
- **이론적 상한가**: 전일 종가 × 1.3 (정확히 30% 상승)
- **실제 상한가**: 이론적 상한가를 **호가 단위로 내림한 값**

### ⚠️ 중요: 29.5%는 무조건 상한가가 아닙니다!
- 호가 단위 때문에 29.85%, 29.95% 등이 상한가일 수 있음
- 반대로 29.5%는 상한가가 아닐 수도 있음
- **정확한 판별이 필요함**

### 호가 단위 기준
```
- 1,000원 미만: 1원 단위
- 1,000원 이상 ~ 5,000원 미만: 5원 단위
- 5,000원 이상 ~ 10,000원 미만: 10원 단위
- 10,000원 이상 ~ 50,000원 미만: 50원 단위
- 50,000원 이상 ~ 100,000원 미만: 100원 단위
- 100,000원 이상 ~ 500,000원 미만: 500원 단위
- 500,000원 이상: 1,000원 단위
```

### 정확한 상한가 계산 공식
```python
def get_limit_up_price(prev_close):
    """정확한 상한가 가격 계산"""
    theoretical = prev_close * 1.3

    # 호가 단위 적용
    if theoretical < 1000:
        tick = 1
    elif theoretical < 5000:
        tick = 5
    elif theoretical < 10000:
        tick = 10
    elif theoretical < 50000:
        tick = 50
    elif theoretical < 100000:
        tick = 100
    elif theoretical < 500000:
        tick = 500
    else:
        tick = 1000

    # 호가 단위로 내림 (정수형 반환)
    return int(theoretical // tick) * tick

# 상한가 판별
limit_up_price = get_limit_up_price(prev_close)
is_limit_up = (current_price == limit_up_price)
```

### 상한가 판별 입력 변수
- **전일 종가 (prev_close)**: 필수, 기준일 전 거래일 종가
- **현재가 (current_price)**: 필수, 판별하고자 하는 가격
- **날짜 독립적**: 특정 날짜에 종속되지 않음, 언제든 사용 가능

### 날짜 무관 범용 상한가 판별 함수
```python
def is_limit_up_universal(prev_close, current_price):
    """
    언제 날짜의 데이터든 상한가 판별 가능

    Args:
        prev_close: 전일 종가 (기준일 -1 거래일)
        current_price: 판별할 가격 (기준일)

    Returns:
        dict: {
            'is_limit_up': bool,  # 상한가 여부
            'limit_up_price': int,  # 계산된 상한가
            'change_rate': float,  # 실제 등락률
            'theoretical_rate': float  # 이론적 등락률
        }
    """

    # 1. 이론적 상한가 계산
    theoretical_limit = prev_close * 1.3

    # 2. 호가 단위 적용
    if theoretical_limit < 1000:
        tick = 1
    elif theoretical_limit < 5000:
        tick = 5
    elif theoretical_limit < 10000:
        tick = 10
    elif theoretical_limit < 50000:
        tick = 50
    elif theoretical_limit < 100000:
        tick = 100
    elif theoretical_limit < 500000:
        tick = 500
    else:
        tick = 1000

    # 3. 실제 상한가 (호가 단위로 내림)
    actual_limit = int(theoretical_limit // tick) * tick

    # 4. 등락률 계산
    change_rate = ((current_price - prev_close) / prev_close) * 100
    theoretical_rate = ((actual_limit - prev_close) / prev_close) * 100

    # 5. 상한가 판별
    is_limit = (current_price == actual_limit)

    return {
        'is_limit_up': is_limit,
        'limit_up_price': actual_limit,
        'change_rate': round(change_rate, 2),
        'theoretical_rate': round(theoretical_rate, 2)
    }
```

### 활용 사례
1. **실시간 모니터링**: 오늘 상한가 종목 찾기
   ```python
   result = is_limit_up_universal(yesterday_close, today_price)
   ```

2. **과거 데이터 분석**: 특정 기간 상한가 종목 통계
   ```python
   # 2023년 데이터도 분석 가능
   result = is_limit_up_universal(prev_close_20230510, price_20230511)
   ```

3. **백테스팅**: 상한가 전략 검증
   ```python
   # DataFrame 전체 데이터에서 상한가 찾기
   for idx, row in df.iterrows():
       if is_limit_up_universal(row['prev_close'], row['current_price'])['is_limit_up']:
           print(f"{row['date']}: {row['ticker']} 상한가!")
   ```

## 📋 주요 기능

### 1. 상한가 종목 탐색
- 코스닥 전 종목 스캔
- 당일 +30% (상한가) 도달 종목 필터링
- 종목명, 종목코드, 현재가, 등락률 수집

### 2. 데이터 수집 시점
- **실행 시간**: 평일 저녁 8시 1분 (애프터장 마감 직후)
- **스케줄링**: Cron 작업으로 자동 실행
- **주말/공휴일**: 실행하지 않음

### 3. Slack 알림
- 상한가 종목 리스트 전송
- 포맷:
  ```
  📈 오늘의 코스닥 상한가 종목 (2024.02.12)

  1. 삼성전자 (005930): 75,000원 (+30.00%)
  2. LG에너지 (373220): 450,000원 (+29.95%)
  ...

  총 5개 종목이 상한가를 기록했습니다.
  ```

## 🛠️ 기술 스택

### 필수 라이브러리
- **pykrx**: 한국 주식 시장 데이터 수집
- **schedule** 또는 **APScheduler**: 스케줄링
- **requests**: Slack 웹훅 통신
- **pandas**: 데이터 처리

### API/데이터 소스
- **KRX (한국거래소)**: pykrx 라이브러리 활용
- 대안:
  - 한국투자증권 OpenAPI
  - 네이버 금융 크롤링
  - KIS Developers API

## 📐 구현 계획

### Phase 1: 데이터 수집 (핵심)
```python
def get_kosdaq_limit_up_stocks_with_history(target_date):
    """
    코스닥 전 종목 중 당일 상한가 종목 조회 + 5거래일 가격 이력

    ⚠️ 중요: 5일이 아닌 5거래일 기준
    - 주말/공휴일 제외
    - 월요일 기준 → 전주 월~금요일 데이터
    - 화요일 기준 → 전주 화~월요일 데이터

    Returns:
        [{
            'ticker': '123456',
            'name': 'ABC바이오',
            'current_price': 15400,
            'change_rate': 29.95,
            'history': [  # 5거래일전부터 1거래일전까지
                {'date': '2024-02-05', 'change_rate': 29.9, 'trading_day': 'D-5'},
                {'date': '2024-02-06', 'change_rate': 10.5, 'trading_day': 'D-4'},
                {'date': '2024-02-07', 'change_rate': -2.1, 'trading_day': 'D-3'},
                {'date': '2024-02-08', 'change_rate': 5.3, 'trading_day': 'D-2'},
                {'date': '2024-02-09', 'change_rate': 15.2, 'trading_day': 'D-1'}
            ],
            'pattern': '과거 상한가 이력',  # 패턴 분석
            'consecutive_limit_ups': 0  # 연속 상한가 일수
        }]
    """
    # pykrx는 자동으로 거래일만 반환
    from pykrx import stock

    # 5거래일 전 데이터 가져오기 (주말 자동 제외)
    df = stock.get_market_ohlcv(start_date, end_date, ticker)
    # df는 거래일만 포함됨
    pass

def analyze_price_pattern(history):
    """
    5거래일 가격 패턴 분석

    Returns:
        - '연속 상한가' (2거래일 이상 연속)
        - '첫 상한가' (5거래일 내 처음)
        - '재상한가' (5거래일 내 상한가 이력 있음)
        - '모멘텀 상승' (계속 상승 중)
    """
    pass
```

### Phase 2: Slack 알림
```python
def send_slack_notification(stocks):
    """
    상한가 종목 리스트를 Slack으로 전송
    """
    pass
```

### Phase 3: 스케줄링 (수동 설정)
```bash
# crontab -e
1 20 * * 1-5 /usr/bin/python3 /path/to/bots/SangddaBot/main.py
```

## 🔧 환경 변수 (.env)

```env
# Slack
SLACK_WEBHOOK=https://hooks.slack.com/services/...

# Google Sheets (선택: 기록용)
GOOGLE_SHEET_ID_SANGDDA=sheet_id_here

# 설정
KOSDAQ_LIMIT_UP_PERCENT=30.0  # 상한가 기준 (%)
NOTIFICATION_TIME=20:01        # 알림 시간
```

## 📊 예상 출력

### Slack 메시지 예시
```
🚀 [2024년 2월 12일 월요일] 코스닥 상한가 종목

🔥 상한가 달성 (5개)

1. ABC바이오 (123456) | 15,400원 | +29.95% 📈
   └ D-1: +15.2% | D-2: +5.3% | D-3: -2.1% | D-4: +10.5% | D-5: +29.9%

2. XYZ테크 (234567) | 8,900원 | +29.99% 📈
   └ D-1: +29.9% | D-2: +25.1% | D-3: +2.8% | D-4: +1.5% | D-5: +3.2%

3. 신약개발 (345678) | 25,300원 | +30.00% 📈
   └ D-1: +8.7% | D-2: +3.5% | D-3: +1.2% | D-4: -3.1% | D-5: -5.2%

4. AI솔루션 (456789) | 12,500원 | +29.87% 📈
   └ D-1: +12.1% | D-2: -8.2% | D-3: -15.3% | D-4: +29.9% | D-5: +29.9%

5. 배터리소재 (567890) | 33,200원 | +29.91% 📈
   └ D-1: +22.3% | D-2: +15.4% | D-3: +8.7% | D-4: +5.3% | D-5: +2.1%

📊 통계
- 총 상한가 종목: 5개
- 평균 거래량: 전일 대비 +450%

#상한가 #코스닥 #투자정보
```

### 간단 버전 (라인 수 줄이기)
```
📈 코스닥 상한가 [2024.02.12 월]

ABC바이오(123456) | 15,400 | +29.95%
└ D-1: +15% | D-2: +5% | D-3: -2% | D-4: +10% | D-5: +29.9%

XYZ테크(234567) | 8,900 | +29.99%
└ D-1: +29.9% | D-2: +25% | D-3: +2% | D-4: +1% | D-5: +3%

신약개발(345678) | 25,300 | +30.00%
└ D-1: +8% | D-2: +3% | D-3: +1% | D-4: -3% | D-5: -5%

총 3개 종목
※ D-1 = 직전 거래일, D-5 = 5거래일전
```

## 📈 추가 기능 (향후 개발)

1. **상한가 근접 종목** (+25% 이상) 별도 표시
2. **테마별 분류** (바이오, IT, 2차전지 등)
3. **거래량 분석** (전일 대비 거래량 증가율)
4. **연속 상한가** 추적 (2일 연속, 3일 연속 등)
5. **Google Sheets 자동 기록**

## ⚠️ 주의사항

1. **시장 휴장일 처리**: 주말/공휴일 체크 로직 필요
2. **API 제한**: 무료 API의 호출 횟수 제한 고려
3. **데이터 정확성**: 장 마감 후 정정 공시 반영 여부
4. **에러 처리**: 네트워크 오류, API 오류 시 재시도 로직

## 🚀 실행 방법

### 수동 실행
```bash
python bots/SangddaBot/main.py
```

### 자동 실행 (Cron 설정)
```bash
# 평일 저녁 8시 1분 실행
crontab -e
1 20 * * 1-5 cd /Users/chulyong/Documents/RecentProjects/Argos && python bots/SangddaBot/main.py
```

## 📝 개발 우선순위

1. ✅ pykrx로 코스닥 전 종목 데이터 수집
2. ✅ 상한가 종목 필터링 로직
3. ✅ Slack 메시지 포맷팅 및 전송
4. ⬜ 에러 처리 및 로깅
5. ⬜ 테스트 코드 작성
6. ⬜ Cron 설정 문서화

---

> **핵심**: 매일 저녁, 오늘의 코스닥 상한가 종목을 놓치지 않고 확인한다.