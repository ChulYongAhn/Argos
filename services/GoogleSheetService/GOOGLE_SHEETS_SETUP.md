# 구글 시트 연동 설정 가이드

## 📋 사전 준비

1. 구글 계정
2. 구글 시트

## 🔧 설정 단계

### 1. 구글 시트 생성

1. [Google Sheets](https://sheets.google.com) 접속
2. **새 스프레드시트** 생성
3. 시트 이름을 "Argos 거래 기록"으로 변경
4. URL에서 시트 ID 복사
   - URL: `https://docs.google.com/spreadsheets/d/[시트ID]/edit`
   - 시트ID 부분만 복사

### 2. 구글 클라우드 서비스 계정 생성

1. [Google Cloud Console](https://console.cloud.google.com) 접속
2. 프로젝트 생성 (또는 기존 프로젝트 사용)
3. **API 및 서비스** → **사용 설정된 API**
4. **API 및 서비스 사용 설정** 클릭
5. "Google Sheets API" 검색 → 사용 설정
6. "Google Drive API" 검색 → 사용 설정

### 3. 서비스 계정 생성

1. **API 및 서비스** → **사용자 인증 정보**
2. **사용자 인증 정보 만들기** → **서비스 계정**
3. 서비스 계정 정보 입력:
   - 이름: `argos-sheet-recorder`
   - ID: 자동 생성됨
4. **만들기 및 계속**
5. 역할은 건너뛰기 (선택사항)
6. **완료**

### 4. 서비스 계정 키 생성

1. 생성된 서비스 계정 클릭
2. **키** 탭 → **키 추가** → **새 키 만들기**
3. **JSON** 선택 → **만들기**
4. JSON 파일이 자동 다운로드됨
5. 파일명을 `argos_credentials.json`으로 변경
6. Argos 프로젝트 폴더에 저장

### 5. 구글 시트에 권한 부여

1. `argos_credentials.json` 파일 열기
2. `"client_email"` 값 복사 (예: `argos@project.iam.gserviceaccount.com`)
3. 구글 시트로 이동
4. **공유** 버튼 클릭
5. 복사한 이메일 주소 붙여넣기
6. **편집자** 권한 부여
7. **전송** 클릭

### 6. .env 파일 설정

```bash
# 구글 시트 설정
GOOGLE_CREDENTIALS_FILE=argos_credentials.json
ARGOS_SHEET_ID=여기에_시트_ID_입력
```

### 7. 필요한 패키지 설치

```bash
pip install gspread google-auth google-auth-oauthlib google-auth-httplib2
```

## 📝 테스트

```python
python google_sheet_recorder.py
```

성공하면 구글 시트에 테스트 거래 기록이 추가됩니다.

## 🔍 문제 해결

### "인증 파일을 찾을 수 없습니다" 오류
- `argos_credentials.json` 파일이 프로젝트 폴더에 있는지 확인
- .env 파일의 `GOOGLE_CREDENTIALS_FILE` 경로 확인

### "권한이 거부되었습니다" 오류
- 구글 시트에 서비스 계정 이메일이 편집자로 추가되었는지 확인
- Google Sheets API와 Google Drive API가 활성화되었는지 확인

### "시트 ID가 필요합니다" 오류
- .env 파일의 `ARGOS_SHEET_ID` 설정 확인
- 시트 URL에서 올바른 ID를 복사했는지 확인

## 📊 시트 구조

### 거래내역 시트
- 모든 매매 기록 저장
- 컬럼: 거래시간, 거래타입, 코인, 심볼, 매수가격, 매도가격, 수량, 매수금액, 매도금액, 수익률, 수익금, 메모

### 일별요약 시트
- 일별 거래 통계
- 컬럼: 날짜, 거래횟수, 승률, 총수익금, 평균수익률, 최고수익, 최대손실, 누적수익금

## 🎯 사용 예시

```python
from google_sheet_recorder import get_recorder

recorder = get_recorder()

# 매수 기록
recorder.record_buy(
    symbol="KRW-BTC",
    coin_name="비트코인",
    price=140000000,
    quantity=0.001
)

# 매도 기록
recorder.record_sell(
    symbol="KRW-BTC",
    coin_name="비트코인",
    price=145000000,
    quantity=0.001,
    sell_type="익절"
)

# 일별 요약 업데이트
recorder.update_daily_summary()
```

## 📱 모바일에서 확인

1. Google Sheets 앱 설치 (iOS/Android)
2. 같은 구글 계정으로 로그인
3. "Argos 거래 기록" 시트 열기
4. 실시간 거래 내역 확인 가능

---

설정이 완료되면 모든 거래가 자동으로 구글 시트에 기록됩니다!