# SimpleGoogleSheetService

극도로 단순한 구글 시트 기록 서비스

## 특징

- **단일 함수**: `Send()` 하나로 모든 작업 처리
- **Zero Configuration**: credentials.json만 있으면 자동 작동
- **안전한 동작**: 시트 자동 생성 안 함, 헤더 보호

## 설정

### 1. 필수 파일

```
services/SimpleGoogleSheetService/
├── credentials.json       # 구글 API 인증 파일 (필수)
└── simple_google_sheet.py
```

### 2. 환경변수 (.env)

```env
GOOGLE_SHEET_ID=your_google_sheet_id_here
```

### 3. 구글 시트 준비

구글 스프레드시트에 필요한 시트들을 미리 생성해두세요:
- 거래내역
- 상한가
- 코인거래
- 시스템로그
- 기타 필요한 시트들...

## 사용법

### 기본 사용

```python
from services.SimpleGoogleSheetService import Send

# 시트명과 데이터 전달
Send("거래내역", "매수", "삼성전자", "70,000", "100주")
Send("상한가", "에코프로", "+29.95%", "거래량: 1,234,567")
Send("코인거래", "BTC", "매수", "140,000,000", "0.001")
```

### 실제 사용 예시

```python
from services.SimpleGoogleSheetService import Send
from datetime import datetime

# 1. 주식 거래 기록
Send("거래내역", "매수", "삼성전자", "70,000", "100주", "-3.2%")
Send("거래내역", "매도", "LG화학", "500,000", "10주", "+5.1%", "익절")

# 2. 상한가 종목 기록 (시간 포함)
now = datetime.now().strftime("%Y-%m-%d %H:%M")
Send("상한가", now, "에코프로", "+29.95%", "거래량: 1,234,567")

# 3. 코인 거래 기록
Send("코인거래", "BTC", "매수", "140,000,000", "0.001", "140,000원")
Send("코인거래", "ETH", "매도", "5,000,000", "0.1", "500,000원", "+3.5%")

# 4. 시스템 로그
current_time = datetime.now().strftime("%H:%M:%S")
Send("시스템로그", current_time, "API 연결", "바이비트", "성공")
```

## 동작 방식

1. **첫 번째 매개변수**: 항상 시트 이름
2. **나머지 매개변수**: 기록할 데이터 (가변 인자)
3. **시트가 없으면**: 에러 메시지 출력, False 반환
4. **성공 시**: 로그 출력, True 반환

## 로그 메시지

### 성공
```
✅ [거래내역] 시트에 기록: 매수 | 삼성전자 | 70,000 | 100주
```

### 실패
```
❌ 시트 '존재하지않는시트'이 존재하지 않습니다. 먼저 시트를 생성해주세요.
❌ 기록할 데이터가 없습니다.
❌ 구글 시트 ID가 없습니다. .env 파일에 GOOGLE_SHEET_ID를 설정하세요.
```

## 주의사항

- 시트는 미리 생성되어 있어야 함 (자동 생성 안 함)
- 헤더는 사용자가 직접 관리
- 타임스탬프 자동 추가 안 함 (필요시 직접 전달)
- 모든 데이터는 문자열로 변환되어 저장

## 테스트

```bash
cd services/SimpleGoogleSheetService
python TEST_GOOGLE_SHEET.py
```

테스트 전 구글 시트에 다음 시트들을 생성해두세요:
- 거래내역
- 상한가
- 코인거래
- 시스템로그