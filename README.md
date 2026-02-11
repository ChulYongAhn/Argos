# Argos - 암호화폐 자동매매 시스템

## 📊 프로젝트 소개

Argos는 24시간 암호화폐 시장을 실시간으로 모니터링하며 자동으로 매수/매도를 수행하는 트레이딩 봇입니다. 시장 변동성을 분석하여 최적의 수익을 추구하는 것을 목표로 합니다.

## 🎯 주요 기능

- **24/7 시장 모니터링**: 암호화폐 시장을 24시간 실시간 감시
- **자동 매매**: 설정된 전략에 따라 자동으로 매수/매도 실행
- **리스크 관리**: 손절매 및 수익 실현 자동화
- **실시간 알림**: 주요 거래 및 시장 이벤트 알림

## 🚀 시작하기

### 필수 요구사항

- Python 3.8 이상
- 거래소 API 키 (Binance, Upbit 등)

### 설치

1. 저장소 클론
```bash
git clone https://github.com/yourusername/Argos.git
cd Argos
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
`.env.example` 파일을 `.env`로 복사하고 API 키를 입력합니다:
```bash
cp .env.example .env
```

`.env` 파일 내용:
```
# 거래소 API Keys
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here
EXCHANGE=binance  # 또는 upbit, bithumb 등

# 트레이딩 설정
INITIAL_INVESTMENT=1000000
MAX_POSITION_SIZE=0.1
STOP_LOSS_PERCENTAGE=5
TAKE_PROFIT_PERCENTAGE=10
```

### 실행

```bash
python main.py
```

## 🔒 보안 주의사항

⚠️ **중요**:
- `.env` 파일은 절대 git에 커밋하지 마세요
- API 키는 안전하게 보관하고 절대 공유하지 마세요
- 거래소에서 API 권한 설정 시 출금 권한은 비활성화하세요
- IP 화이트리스트 설정을 권장합니다

## 📁 프로젝트 구조

```
Argos/
├── main.py              # 메인 실행 파일
├── .env                 # API 키 및 환경 설정 (git 제외)
├── .env.example         # 환경 변수 예시 파일
├── .gitignore          # Git 제외 파일 목록
├── requirements.txt     # Python 패키지 의존성
└── README.md           # 프로젝트 문서
```

## ⚙️ 설정

프로그램의 세부 동작은 `.env` 파일을 통해 설정할 수 있습니다:

- **거래 간격**: 시장 체크 주기
- **포지션 크기**: 각 거래의 최대 투자 비율
- **손절/익절 비율**: 자동 청산 기준점

## 📈 거래 전략

Argos는 다음과 같은 전략을 사용합니다:
- 기술적 지표 기반 신호 포착
- 거래량 분석
- 가격 패턴 인식
- 리스크 관리 시스템

## 🤝 기여하기

프로젝트 개선에 관심이 있으시다면 Issue를 등록하거나 Pull Request를 보내주세요.

## 📝 라이센스

이 프로젝트는 MIT 라이센스 하에 있습니다.

## ⚠️ 면책 조항

암호화폐 거래는 높은 위험을 동반합니다. 이 프로그램을 사용함으로써 발생하는 모든 손실에 대해 개발자는 책임지지 않습니다. 투자 전 충분한 연구와 테스트를 진행하세요.

---

**개발자**: Your Name
**문의**: your.email@example.com