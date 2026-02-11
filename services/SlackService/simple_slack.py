"""
심플 슬랙 서비스 - 어떤 프로젝트에서도 수정 없이 사용 가능 -



"""

#* 사용지침
#이것 사용할때 어떤 프로젝트인지 명시할것 ex) [Argos] 비트코인 매수완료 , [ChulAutoStock] 주식 검색 시작 등등

import os
import requests
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


class SimpleSlack:
    """심플 슬랙 서비스"""

    def __init__(self, webhook_url: Optional[str] = None):
        """
        초기화

        Args:
            webhook_url: Slack Webhook URL (없으면 .env에서 SLACK_WEBHOOK 읽음)
        """
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK")
        self.enabled = bool(self.webhook_url)

        if not self.enabled:
            print("⚠️ Slack 웹훅이 설정되지 않음")

    def send(self, message: str) -> bool:
        """
        슬랙 메시지 전송

        Args:
            message: 전송할 메시지

        Returns:
            전송 성공 여부
        """
        if not self.enabled:
            return False

        try:
            # 타임스탬프 추가
            time_str = datetime.now().strftime("%H:%M:%S")
            full_message = f"[{time_str}] {message}"

            response = requests.post(
                self.webhook_url,
                json={"text": full_message},
                headers={"Content-Type": "application/json"}
            )

            return response.status_code == 200

        except Exception as e:
            print(f"❌ Slack 전송 실패: {e}")
            return False


# 전역 인스턴스
_slack = None


def get_slack(webhook_url: Optional[str] = None) -> SimpleSlack:
    """슬랙 인스턴스 반환"""
    global _slack
    if _slack is None:
        _slack = SimpleSlack(webhook_url)
    return _slack


def slack(message: str, webhook_url: Optional[str] = None) -> bool:
    """
    간편 슬랙 전송 함수

    Args:
        message: 전송할 메시지
        webhook_url: Slack Webhook URL (선택)

    Returns:
        전송 성공 여부

    Examples:
        >>> slack("프로그램 시작")
        >>> slack("매수 완료: BTC 0.001개")
        >>> slack("에러 발생!", "https://hooks.slack.com/...")
    """
    return get_slack(webhook_url).send(message)


# 테스트
if __name__ == "__main__":
    # 방법 1: 함수로 바로 사용
    slack("🎉 테스트 메시지입니다")

    # 방법 2: 클래스로 사용
    s = SimpleSlack()
    s.send("📢 클래스로 보내는 메시지")

    # 방법 3: 웹훅 직접 전달
    # slack("메시지", "https://hooks.slack.com/services/...")