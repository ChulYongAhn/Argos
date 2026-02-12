# 🚀 Argos - Personal Project Playground

> 개인 프로젝트를 위한 통합 작업 공간. Unity 프로젝트처럼 각 봇(Scene)은 독립적으로 실행되며 공통 서비스(Resources)를 공유합니다.

## 📁 구조

```
Argos/
├── bots/                  # 독립 프로젝트들 (Unity의 Scenes)
│   ├── ObCoinBot/         # 오비 코인 자동매매
│   └── SangddaBot/        # 상따봇 (상한가 따라가기)
├── services/              # 공통 서비스 (Unity의 Resources)
│   ├── SlackService/      # Slack 알림
│   └── GoogleSheetService/# Google Sheets 기록
└── .env                   # API 키 및 설정 (git 제외)
```

## 🚀 빠른 시작

### 새 프로젝트 만들기

```python
# bots/my_bot/main.py
import os
from dotenv import load_dotenv
from services.SlackService import slack
from services.GoogleSheetService import record

load_dotenv()  # .env 로드

def main():
    # Slack 알림
    slack("봇 시작!")

    # Google Sheets 기록
    sheet_id = os.getenv('GOOGLE_SHEET_ID_1')
    record(sheet_id, "데이터1", "데이터2")

if __name__ == "__main__":
    main()
```

### 실행

```bash
python bots/my_bot/main.py
```

## ⚙️ 환경 설정

### .env 파일
```env
# API 키
UPBIT_ACCESS_KEY=your_key
SLACK_WEBHOOK=https://hooks.slack.com/...

# Google Sheets ID
GOOGLE_SHEET_ID_1=sheet_id_here
GOOGLE_SHEET_ID_2=another_sheet_id
```

### 개발 환경
- **Python**: 3.13.1
- **OS**: macOS
- **가상환경**: conda (필수)
- **설치 가이드**: setup.md 참조

## 📋 핵심 원칙

1. **독립성**: 각 봇은 완전히 독립적 (서로 영향 없음)
2. **보안**: 민감정보는 `.env`에만 (절대 git에 올리지 않음)
3. **재사용**: services 폴더의 기능은 모든 프로젝트에서 사용
4. **확장성**: 새 봇/서비스 언제든 추가 가능

## 🎯 Unity와 비교

| Argos | Unity |
|-------|-------|
| `bots/` | Scenes |
| `services/` | Resources |
| `.env` | ProjectSettings |
| `main.py` | GameManager |

---

> **철학**: "새로운 아이디어가 있을 때, Argos에서 바로 시작하자"