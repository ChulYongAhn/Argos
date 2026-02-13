"""
상따봇 DART + KRX 통합 공시 테스트
"""
import os
import sys

# Argos 루트 경로를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.DartService.dart_service import GetDartData
from services.KrxService.krx_simple import GetKrxWarnings

def test_combined_disclosures():
    """통합 공시 테스트"""

    test_stocks = [
        ('187660', '현대ADM'),
        ('089980', '상아프론테크')
    ]

    print("="*60)
    print("📢 상따봇 DART + KRX 통합 공시 테스트")
    print("="*60)

    for ticker, name in test_stocks:
        print(f"\n🔥 {name} ({ticker})")
        print("-"*40)

        # DART 공시
        print("\n📄 DART 공시 조회 중...")
        dart_disclosures = GetDartData(ticker, 15)

        if dart_disclosures:
            print(f"✅ DART 공시 {len(dart_disclosures)}개:")
            for i, disc in enumerate(dart_disclosures[:3], 1):
                date_str = disc['date'][4:6] + '/' + disc['date'][6:8] if disc['date'] else ''
                title = disc['title'][:50] + ('...' if len(disc['title']) > 50 else '')
                print(f"  {i}. {date_str} {title}")
        else:
            print("❌ DART 공시 없음")

        # KRX 공시
        print("\n⚠️ KRX 경고 조회 중...")
        krx_warnings = GetKrxWarnings(ticker)

        if krx_warnings:
            print(f"✅ KRX 경고 {len(krx_warnings)}개:")
            for i, warning in enumerate(krx_warnings, 1):
                date_str = warning['date'][4:6] + '/' + warning['date'][6:8] if warning['date'] else ''
                print(f"  {i}. 🚨 {date_str} {warning['title']}")
        else:
            print("❌ KRX 경고 없음")

    print("\n" + "="*60)
    print("✨ 테스트 완료")
    print("="*60)

    print("\n💡 슬랙 메시지 형식 예시:")
    print("-"*40)
    print("🔥 *현대ADM(187660) | 7,380 | +29.93%*")
    print("└ D-1: +29.98% | D-2: +3.8% | ...")
    print("└ ⚠️ KRX 경고 (1개):")
    print("     🚨 02/13 투자주의종목 지정")
    print("└ 📢 DART 공시 (1개):")
    print("     👥 02/10 임원ㆍ주요주주특정증권등소유상황보고서")

if __name__ == "__main__":
    test_combined_disclosures()