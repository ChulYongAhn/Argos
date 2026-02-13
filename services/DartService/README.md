# 📊 DART Service

DART 전자공시 시스템 API 서비스

## 📌 주요 기능

- **공시 조회**: 날짜, 기업, 공시유형별 조회
- **키워드 검색**: 특정 키워드가 포함된 공시 검색
- **단기과열종목**: 단기과열종목 예고 공시 추적
- **실시간 모니터링**: 오늘의 공시 조회

## 🚀 빠른 시작

### 1. API 키 발급

1. [DART OpenAPI](https://opendart.fss.or.kr/) 접속
2. 회원가입 및 로그인
3. 'API 키 발급' 메뉴에서 키 발급
4. `.env` 파일에 추가:
```env
DART_API_KEY=your_dart_api_key_here
```

### 2. 기본 사용법

```python
from services.DartService import (
    get_today_disclosures,
    search_keyword,
    get_overheat_warnings
)

# 오늘의 코스닥 공시
disclosures = get_today_disclosures('K')

# 키워드 검색
results = search_keyword('상한가', days_back=7)

# 단기과열종목 예고
warnings = get_overheat_warnings()
```

## 📖 API 상세

### `get_disclosures()`
모든 파라미터를 지정하여 공시 검색

```python
disclosures = get_disclosures(
    corp_code='00187660',      # 기업코드
    bgn_de='20260201',          # 시작일
    end_de='20260213',          # 종료일
    corp_cls='K',               # K:코스닥, Y:유가증권
    pblntf_ty='B',              # A:정기, B:주요사항
    page_count=100              # 페이지당 건수
)
```

### `get_today_disclosures()`
오늘의 공시 조회

```python
# 코스닥 공시
kosdaq = get_today_disclosures('K')

# 코스피 공시
kospi = get_today_disclosures('Y')
```

### `search_keyword()`
키워드로 공시 검색

```python
# 최근 7일간 '단기과열' 키워드
results = search_keyword('단기과열', days_back=7)

# 최근 30일간 '상한가' 키워드
results = search_keyword('상한가', days_back=30)
```

### `get_overheat_warnings()`
단기과열종목 예고 조회

```python
warnings = get_overheat_warnings()
for w in warnings:
    print(f"{w['corp_name']}: {w['report_nm']}")
```

## 🔧 고급 사용법

### DartService 클래스 직접 사용

```python
from services.DartService import DartService

# 인스턴스 생성
dart = DartService(api_key='your_key')

# 기업코드 조회
corp_code = dart.get_corp_code('187660')

# 공시 포맷팅
formatted = dart.format_disclosure(disclosure_dict)
print(formatted)
```

## 📊 공시 유형

### pblntf_ty (공시유형)
- `A`: 정기공시
- `B`: 주요사항보고
- `C`: 발행공시
- `D`: 지분공시
- `E`: 기타공시
- `F`: 외부감사관련
- `G`: 펀드공시
- `H`: 자산유동화
- `I`: 거래소공시
- `J`: 공정위공시

### corp_cls (법인구분)
- `Y`: 유가증권시장
- `K`: 코스닥
- `N`: 코넥스
- `E`: 기타

## 🎯 활용 예시

### 상따봇과 연동

```python
# bots/SangddaBot/Starter.py
from services.DartService import get_overheat_warnings

# 단기과열종목 체크
warnings = get_overheat_warnings()
overheat_stocks = [w['stock_code'] for w in warnings]

# 상한가 종목에서 제외
for stock in limit_up_stocks:
    if stock['ticker'] not in overheat_stocks:
        # 안전한 종목만 처리
        process_stock(stock)
```

### 공시 알림 봇

```python
from services.SlackService import slack
from services.DartService import get_today_disclosures

# 매일 오전 9시 실행
disclosures = get_today_disclosures('K')

for disc in disclosures:
    if '단기과열' in disc['report_nm']:
        message = f"⚠️ {disc['corp_name']}: {disc['report_nm']}"
        slack(message)
```

## ⚠️ 주의사항

1. **API 제한**: 일일 10,000건 제한
2. **기업코드**: 종목코드와 다름 (매핑 필요)
3. **응답 지연**: 대량 조회 시 timeout 설정 필요

## 📚 참고 자료

- [DART OpenAPI 가이드](https://opendart.fss.or.kr/guide/main.do)
- [API 명세서](https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001)

## 🧪 테스트

```bash
cd services/DartService
python TEST_DART.py
```

---

**Note**: 실제 사용을 위해서는 DART OpenAPI 키가 필요합니다.