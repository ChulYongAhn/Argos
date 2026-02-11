"""
구글 시트 테스트 파일
simple_google_sheet을 사용한 범용 기록 테스트
"""

from simple_google_sheet import record, record_dict, get_sheet
from datetime import datetime
import time

def test_google_sheet():
    """구글 시트 범용 기록 테스트"""

    print("=" * 50)
    print("🚀 구글 시트 테스트 시작")
    print("=" * 50)

    # 1. 가변 인자 테스트 - 원하는 만큼 인자 전달
    print("\n[테스트 1: 가변 인자]")
    record("테스트1")
    record("테스트2", "데이터A")
    record("테스트3", "데이터A", "데이터B")
    record("테스트4", "데이터A", "데이터B", "데이터C")
    record("테스트5", "A", "B", "C", "D", "E", "F", "G")
    print("✅ 가변 인자 테스트 완료")

    time.sleep(1)

    # 2. 거래 시뮬레이션
    print("\n[테스트 2: 거래 기록]")
    record("매수", "비트코인", "KRW-BTC", 140000000, 0.001, 140000)
    record("매도", "비트코인", "KRW-BTC", 145000000, 0.001, 145000, "+3.6%", "+5000")
    record("매수", "이더리움", "KRW-ETH", 5000000, 0.1, 500000)
    record("매도", "이더리움", "KRW-ETH", 4800000, 0.1, 480000, "-4.0%", "-20000")
    print("✅ 거래 기록 완료")

    time.sleep(1)

    # 3. 시스템 로그
    print("\n[테스트 3: 시스템 로그]")
    record("시스템", "시작", "Argos v1.0")
    record("API", "연결", "업비트", "성공")
    record("에러", "API", "Rate limit", "429", "1분 대기")
    record("알림", "슬랙", "메시지 전송", "성공")
    print("✅ 시스템 로그 완료")

    time.sleep(1)

    # 4. 딕셔너리 기록 (헤더 자동 관리)
    print("\n[테스트 4: 딕셔너리 기록]")
    record_dict({
        "종목": "리플",
        "심볼": "KRW-XRP",
        "거래": "매수",
        "가격": 3500,
        "수량": 100,
        "금액": 350000
    })

    record_dict({
        "종목": "솔라나",
        "심볼": "KRW-SOL",
        "거래": "매도",
        "가격": 250000,
        "수량": 2,
        "금액": 500000,
        "수익률": "+5.2%",
        "메모": "목표가 도달"
    })

    # 새로운 필드 추가 테스트
    record_dict({
        "종목": "카르다노",
        "심볼": "KRW-ADA",
        "거래": "매수",
        "가격": 800,
        "수량": 1000,
        "금액": 800000,
        "RSI": 28.5,  # 새 필드
        "볼륨": 12345678  # 새 필드
    })
    print("✅ 딕셔너리 기록 완료")

    # 5. 일일 요약
    print("\n[테스트 5: 일일 요약]")
    record("="*20, "일일 요약", "="*20)
    record("거래횟수", "15", "승률", "60%", "수익금", "+125,000원")
    print("✅ 일일 요약 완료")

    # URL 출력
    sheet = get_sheet()
    print(f"\n📱 구글 시트 URL: {sheet.get_sheet_url()}")
    print("✅ 구글 시트에서 확인하세요!")

    print("\n" + "=" * 50)
    print("✨ 모든 테스트 완료!")
    print("=" * 50)


if __name__ == "__main__":
    test_google_sheet()