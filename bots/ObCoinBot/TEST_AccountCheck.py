"""
TEST_AccountCheck - 바이비트 계정 잔액 조회 테스트
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


def check_balance():
    """바이비트 계정 잔액 조회"""
    api_key = os.getenv('BYBIT_API_KEY')
    api_secret = os.getenv('BYBIT_API_SECRET')

    if not api_key or not api_secret:
        print("⚠️  바이비트 API 키를 .env 파일에 설정해주세요!")
        print("   BYBIT_API_KEY=실제API키")
        print("   BYBIT_API_SECRET=실제시크릿키")
        return

    # 바이비트 클라이언트 초기화 (메인넷)
    client = HTTP(
        testnet=False,
        api_key=api_key,
        api_secret=api_secret
    )

    print("🚀 바이비트 계정 조회 테스트")
    print("-" * 50)

    try:
        # 통합 계정 잔액 조회
        result = client.get_wallet_balance(
            accountType="UNIFIED"  # 통합 계정
        )

        if result['retCode'] != 0:
            print(f"❌ API 오류: {result['retMsg']}")
            return

        # 현재 시간
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n⏰ 조회 시간: {now}")
        print("=" * 50)

        # 계정 정보
        account_info = result['result']['list'][0]

        # 총 자산 (USD)
        total_equity = float(account_info.get('totalEquity', 0))
        total_wallet_balance = float(account_info.get('totalWalletBalance', 0))

        print(f"💰 총 자산: ${total_equity:,.2f}")
        print(f"💵 지갑 잔액: ${total_wallet_balance:,.2f}")
        print("-" * 50)

        # 코인별 잔액
        coins = account_info.get('coin', [])
        if coins:
            print("\n📊 코인별 잔액:")
            print(f"{'코인':<10} {'잔액':>15} {'USD 가치':>15}")
            print("-" * 40)

            for coin in coins:
                symbol = coin['coin']
                wallet_balance = float(coin.get('walletBalance', 0))
                usd_value = float(coin.get('usdValue', 0))

                if wallet_balance > 0:  # 잔액이 있는 코인만 표시
                    print(f"{symbol:<10} {wallet_balance:>15.6f} ${usd_value:>14.2f}")

        print("\n" + "=" * 50)
        print("✅ 조회 완료")

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")


if __name__ == "__main__":
    check_balance()