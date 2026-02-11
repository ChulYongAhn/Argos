# SlackService

간단한 슬랙 알림 서비스 패키지

## 설치

이 폴더를 프로젝트에 복사

## 사용법

```python
from services.SlackService import slack

# 간단 사용
slack("메시지 전송!")
```

## 설정

`.env` 파일에 추가:
```
SLACK_WEBHOOK=your_webhook_url_here
```

## 특징

- 자동 타임스탬프
- 최소한의 의존성
- 어떤 프로젝트에서도 사용 가능