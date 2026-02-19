"""
TEST_BUY - 바이비트 비트코인 구매 테스트
최소 주문 금액(5 USDT)으로 BTC 구매
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from pybit.unified_trading import HTTP

# 프로젝트 루트 패스 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# .env 파일 로드
load_dotenv()


def buy_btc_test():
    """비트코인 최소 금액 구매 테스트"""
    api_key = os.getenv('BYBIT_API_KEY')
    api_secret = os.getenv('BYBIT_API_SECRET')

    if not api_key or not api_secret:
        print("⚠️  바이비트 API 키를 .env 파일에 설정해주세요!")
        return

    # 바이비트 클라이언트 초기화 (메인넷)
    client = HTTP(
        testnet=False,
        api_key=api_key,
        api_secret=api_secret
    )

    print("🛒 비트코인 구매 테스트")
    print("-" * 50)

    try:
        # 1. 현재 BTC 가격 조회
        ticker = client.get_tickers(
            category="spot",
            symbol="BTCUSDT"
        )

        btc_price = float(ticker['result']['list'][0]['lastPrice'])
        print(f"📊 현재 BTC 가격: ${btc_price:,.2f}")

        # 2. 최소 주문 금액 계산 (바이비트 최소 10 USDT 권장)
        # 바이비트 BTCUSDT 최소 주문은 실제로 10 USDT 정도
        order_amount_usdt = 10.0  # 10 USDT (안전한 최소 금액)
        order_amount_btc = order_amount_usdt / btc_price

        # 소수점 6자리로 반올림 (바이비트 정밀도)
        order_amount_btc = round(order_amount_btc, 6)

        print(f"💰 구매 금액: ${order_amount_usdt}")
        print(f"📦 구매 수량: {order_amount_btc:.6f} BTC")
        print("-" * 50)

        # 3. 시장가 구매 주문 (USDT 금액으로 주문)
        print("📤 주문 전송 중...")

        # 바이비트 시장가 매수는 marketUnit="quoteCoin"으로 USDT 금액 지정
        order_result = client.place_order(
            category="spot",
            symbol="BTCUSDT",
            side="Buy",
            orderType="Market",
            qty=str(order_amount_usdt),  # USDT 금액으로 주문
            marketUnit="quoteCoin"  # USDT로 주문 (중요!)
        )

        if order_result['retCode'] == 0:
            order_id = order_result['result']['orderId']
            print(f"✅ 구매 주문 성공!")
            print(f"📋 주문 ID: {order_id}")

        else:
            print(f"❌ 주문 실패: {order_result['retMsg']}")

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        print("\n💡 팁:")
        print("  - 계정에 USDT 잔액이 있는지 확인하세요")
        print("  - API 권한에 'Trade' 권한이 있는지 확인하세요")
        print("  - 최소 주문 금액은 10 USDT입니다")


if __name__ == "__main__":
    buy_btc_test()