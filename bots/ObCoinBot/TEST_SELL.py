"""
TEST_SELL - 바이비트 비트코인 판매 테스트
최소 주문 금액(5 USDT)으로 BTC 판매
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


def sell_btc_test():
    """비트코인 최소 금액 판매 테스트"""
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

    print("💸 비트코인 판매 테스트")
    print("-" * 50)

    try:
        # 1. 현재 BTC 잔액 확인
        balance_result = client.get_wallet_balance(
            accountType="UNIFIED"
        )

        btc_balance = 0
        if balance_result['retCode'] == 0:
            for coin in balance_result['result']['list'][0]['coin']:
                if coin['coin'] == 'BTC':
                    btc_balance = float(coin.get('walletBalance', 0))
                    break

        print(f"💰 현재 BTC 잔액: {btc_balance:.6f} BTC")

        if btc_balance < 0.000001:
            print("❌ BTC 잔액이 부족합니다. 먼저 TEST_BUY.py를 실행하세요.")
            return

        # 2. 현재 BTC 가격 조회
        ticker = client.get_tickers(
            category="spot",
            symbol="BTCUSDT"
        )

        btc_price = float(ticker['result']['list'][0]['lastPrice'])
        print(f"📊 현재 BTC 가격: ${btc_price:,.2f}")

        # 3. 최소 주문 금액 계산 (10 USDT 상당의 BTC)
        order_amount_usdt = 10.0  # 10 USDT (안전한 최소 금액)
        order_amount_btc = order_amount_usdt / btc_price

        # 소수점 6자리로 반올림 (바이비트 정밀도)
        order_amount_btc = round(order_amount_btc, 6)

        # 잔액이 부족한 경우 잔액 전체 판매
        if order_amount_btc > btc_balance:
            order_amount_btc = round(btc_balance * 0.99, 6)  # 수수료 고려해서 99%만 판매
            print(f"⚠️  잔액 부족으로 {order_amount_btc:.6f} BTC만 판매합니다.")

        print(f"💸 판매 수량: {order_amount_btc:.6f} BTC")
        print(f"💵 예상 수령액: ${order_amount_btc * btc_price:.2f}")
        print("-" * 50)

        # 4. 시장가 판매 주문
        print("📤 주문 전송 중...")

        order_result = client.place_order(
            category="spot",
            symbol="BTCUSDT",
            side="Sell",
            orderType="Market",
            qty=str(order_amount_btc)  # BTC 수량으로 주문
        )

        if order_result['retCode'] == 0:
            order_id = order_result['result']['orderId']
            print(f"✅ 판매 주문 성공!")
            print(f"📋 주문 ID: {order_id}")

        else:
            print(f"❌ 주문 실패: {order_result['retMsg']}")

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        print("\n💡 팁:")
        print("  - 계정에 BTC 잔액이 있는지 확인하세요")
        print("  - API 권한에 'Trade' 권한이 있는지 확인하세요")
        print("  - 먼저 TEST_BUY.py로 BTC를 구매하세요")


if __name__ == "__main__":
    sell_btc_test()