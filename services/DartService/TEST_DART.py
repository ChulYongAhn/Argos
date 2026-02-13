"""
DART 서비스 테스트
"""

from dart_service import GetDartData


def test_get_dart_data():
    """GetDartData 함수 테스트"""

    print("=" * 60)
    print("🚀 DART 전자공시 서비스 테스트 (GetDartData)")
    print("=" * 60)

    # 테스트 종목: 삼성전자 (005930)
    print("\n[테스트 1: 삼성전자 7일치 공시]")
    stock_code = "005930"
    days = 7

    disclosures = GetDartData(stock_code, days)

    if disclosures:
        print(f"✅ {len(disclosures)}개 공시 발견")
        for i, disc in enumerate(disclosures[:5], 1):
            print(f"\n{i}. {disc.get('title', '')}")
            print(f"   날짜: {disc.get('date', '')}")
            print(f"   링크: {disc.get('link', '')}")
    else:
        print(f"⚠️ {stock_code} 종목의 공시가 없습니다.")

    # 테스트 종목 2: 현대ADM (187660) - 코스닥
    print("\n[테스트 2: 현대ADM 15일치 공시]")
    stock_code = "187660"
    days = 15

    disclosures = GetDartData(stock_code, days)

    if disclosures:
        print(f"✅ {len(disclosures)}개 공시 발견")
        for i, disc in enumerate(disclosures[:5], 1):
            print(f"\n{i}. {disc.get('title', '')}")
            print(f"   날짜: {disc.get('date', '')}")
            print(f"   링크: {disc.get('link', '')}")
    else:
        print(f"⚠️ {stock_code} 종목의 공시가 없습니다.")

    # 에러 테스트
    print("\n[테스트 3: 빈 종목코드 테스트]")
    disclosures = GetDartData("", 7)
    print(f"결과: {len(disclosures)}개")

    print("\n" + "=" * 60)
    print("✨ 테스트 완료!")
    print("=" * 60)


if __name__ == "__main__":
    print("📌 DART API 키가 필요합니다!")
    print("   .env 파일에 DART_API_KEY 설정 확인\n")

    test_get_dart_data()