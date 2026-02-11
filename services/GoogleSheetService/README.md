# GoogleSheetService

범용 구글 시트 기록 서비스 패키지

## 📦 패키지 구조

```
GoogleSheetService/
├── __init__.py                   # 패키지 초기화
├── simple_google_sheet.py        # 범용 구글 시트 레코더
├── google_sheet_recorder.py      # Argos 전용 레코더
├── credentials_template.json     # 인증 파일 템플릿
├── GOOGLE_SHEETS_SETUP.md       # 상세 설정 가이드
├── .gitignore                   # 인증 파일 제외
└── README.md                     # 이 파일
```

## 🚀 빠른 시작

### 1. 패키지 복사
이 폴더 전체를 프로젝트에 복사

### 2. 패키지 설치
```bash
pip install gspread google-auth
```

### 3. Google 인증 설정
1. Google Cloud Console에서 서비스 계정 생성
2. JSON 키 다운로드
3. 다운로드한 파일을 `credentials.json`으로 저장
4. 상세 가이드: [GOOGLE_SHEETS_SETUP.md](GOOGLE_SHEETS_SETUP.md) 참고

### 4. .env 설정
```env
GOOGLE_SHEET_ID=your_sheet_id_here
GOOGLE_CREDENTIALS_FILE=credentials.json
```

## 💡 사용법

### 가변 인자 방식 (Simple)
```python
from GoogleSheetService import record

# 원하는 만큼 인자 전달
record("A")
record("A", "B")
record("A", "B", "C", "D", "E")
record("매수", "비트코인", 140000000, 0.001)
```

### 딕셔너리 방식
```python
from GoogleSheetService import record_dict

record_dict({
    "종목": "비트코인",
    "가격": 140000000,
    "수량": 0.001
})
```

### 클래스 직접 사용
```python
from GoogleSheetService import SimpleGoogleSheet

sheet = SimpleGoogleSheet(sheet_id="your_id")
sheet.record("데이터1", "데이터2", "데이터3")
```

## ✨ 특징

- 🕐 자동 타임스탬프
- 📝 가변 인자 지원 (Unity params처럼)
- 📊 헤더 자동 관리
- 🔧 어떤 프로젝트에서도 사용 가능
- 🚫 외부 의존성 없음 (SlackService 독립)