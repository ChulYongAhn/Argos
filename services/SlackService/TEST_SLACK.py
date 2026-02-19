"""
슬랙 메시지 테스트 파일
simple_slack을 사용해서 다양한 메시지를 전송하는 예제
"""

from simple_slack import slack
from datetime import datetime
import time

def test_slack_messages():
    """다양한 슬랙 메시지 테스트"""

    print("=" * 50)
    print("🚀 슬랙 메시지 테스트 시작")
    print("=" * 50)

    # 1. 시작 메시지
    if slack("🎉 Argos 슬랙 테스트 시작!"):
        print("✅ 시작 메시지 전송 성공")
    else:
        print("❌ 시작 메시지 전송 실패 - .env 파일의 SLACK_WEBHOOK 확인 필요")
        return

    time.sleep(1)

    # 2. 시스템 상태 메시지
    slack("💻 시스템 상태: 정상 작동 중")
    print("✅ 시스템 상태 메시지 전송")

    time.sleep(1)

    # 3. 거래 시뮬레이션 메시지
    slack("🛒 [매수] 비트코인(KRW-BTC) 1,000,000원 매수 완료")
    print("✅ 매수 메시지 전송")

    time.sleep(1)

    slack("💰 [매도] 이더리움(KRW-ETH) 500,000원 매도 완료 (수익률: +5.2%)")
    print("✅ 매도 메시지 전송")

    time.sleep(1)

    # 4. 에러 메시지
    slack("⚠️ [경고] API 응답 지연 감지 (3초 초과)")
    print("✅ 경고 메시지 전송")

    time.sleep(1)

    slack("🚨 [에러] 바이비트 API 연결 실패 - Rate limit exceeded")
    print("✅ 에러 메시지 전송")

    time.sleep(1)

    # 5. 리포트 메시지
    report = f"""
📊 일일 거래 리포트
━━━━━━━━━━━━━━━━
• 총 거래: 15회
• 매수: 8회 / 매도: 7회
• 일일 수익률: +3.8%
• 총 평가금액: 10,523,000원
━━━━━━━━━━━━━━━━
"""
    slack(report)
    print("✅ 일일 리포트 전송")

    time.sleep(1)

    # 6. 마켓 정보
    slack("📈 급등 감지: XRP +15.3% (거래량 200% 증가)")
    print("✅ 마켓 알림 전송")

    time.sleep(1)

    # 7. 종료 메시지
    slack(f"🏁 테스트 완료 - 총 9개 메시지 전송 완료")
    print("✅ 종료 메시지 전송")

    print("\n" + "=" * 50)
    print("✨ 모든 테스트 메시지 전송 완료!")
    print("Slack 채널을 확인해보세요.")
    print("=" * 50)


if __name__ == "__main__":
    test_slack_messages()