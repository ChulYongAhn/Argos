# SimpleGoogleSheetService 설정 가이드

## 📋 사전 준비

1. 구글 계정
2. 구글 스프레드시트

## 🔧 설정 단계

### 1. 구글 스프레드시트 생성

1. [Google Sheets](https://sheets.google.com) 접속
2. **새 스프레드시트** 생성
3. 스프레드시트 이름 지정
4. 필요한 시트(탭) 생성:
   - 예: 거래내역, 상한가, 코인거래, 시스템로그 등
5. URL에서 시트 ID 복사
   - URL: `https://docs.google.com/spreadsheets/d/[시트ID]/edit`
   - [시트ID] 부분만 복사

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
   - 이름: 원하는 이름 (예: `sheet-service`)
   - ID: 자동 생성됨
4. **만들기 및 계속**
5. 역할은 건너뛰기 (선택사항)
6. **완료**

### 4. 서비스 계정 키 생성

1. 생성된 서비스 계정 클릭
2. **키** 탭 → **키 추가** → **새 키 만들기**
3. **JSON** 선택 → **만들기**
4. JSON 파일이 자동 다운로드됨
5. 파일명을 `credentials.json`으로 변경
6. `services/SimpleGoogleSheetService/` 폴더에 저장

### 5. 구글 시트에 권한 부여

1. `credentials.json` 파일 열기
2. `"client_email"` 필드의 이메일 주소 복사
   - 예: `sheet-service@project-name.iam.gserviceaccount.com`
3. 구글 스프레드시트 열기
4. 우측 상단 **공유** 버튼 클릭
5. 복사한 이메일 주소 붙여넣기
6. **편집자** 권한 부여
7. **보내기** 클릭

### 6. 환경 변수 설정

`.env` 파일에 시트 ID 추가:

```env
GOOGLE_SHEET_ID=복사한_시트_ID_붙여넣기
```

## ✅ 설정 완료!

이제 Send 함수를 사용할 수 있습니다:

```python
from services.SimpleGoogleSheetService import Send

Send("시트이름", "데이터1", "데이터2", "데이터3")
```