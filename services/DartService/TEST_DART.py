"""
DART 서비스 테스트
"""

from dart_service import (
    get_dart,
    get_today_disclosures,
    search_keyword,
    get_overheat_warnings
)
from datetime import datetime
import time


def test_dart_service():
    """DART 서비스 테스트"""

    print("=" * 60)
    print("🚀 DART 전자공시 서비스 테스트")
    print("=" * 60)

    try:
        # 1. 서비스 초기화 테스트
        print("\n[테스트 1: 서비스 초기화]")
        dart = get_dart()
        print("✅ DART 서비스 초기화 성공")

    except ValueError as e:
        print(f"❌ 초기화 실패: {e}")
        print("\n💡 해결 방법:")
        print("1. .env 파일에 DART_API_KEY 추가")
        print("2. https://opendart.fss.or.kr/ 에서 API 키 발급")
        return

    # 2. 오늘의 공시 조회
    print("\n[테스트 2: 오늘의 코스닥 공시]")
    today_disclosures = get_today_disclosures('K')

    if today_disclosures:
        print(f"✅ {len(today_disclosures)}개 공시 발견")
        for i, disc in enumerate(today_disclosures[:5], 1):
            print(f"\n{i}. {disc.get('corp_name', '')} ({disc.get('stock_code', '')})")
            print(f"   {disc.get('report_nm', '')}")
            print(f"   제출: {disc.get('rcept_dt', '')}")
    else:
        print("오늘은 공시가 없거나 API 오류입니다.")

    time.sleep(1)  # API 부하 방지

    # 3. 키워드 검색 테스트
    print("\n[테스트 3: 키워드 검색 - '상한가']")
    keyword_results = search_keyword('상한가', days_back=7)

    if keyword_results:
        print(f"✅ '상한가' 관련 공시 {len(keyword_results)}개 발견")
        for disc in keyword_results[:3]:
            print(f"\n• {disc.get('corp_name', '')} - {disc.get('report_nm', '')}")
    else:
        print("'상한가' 관련 공시가 없습니다.")

    time.sleep(1)

    # 4. 단기과열종목 예고 조회
    print("\n[테스트 4: 단기과열종목 예고]")
    overheat_warnings = get_overheat_warnings()

    if overheat_warnings:
        print(f"⚠️ 단기과열종목 예고 {len(overheat_warnings)}개")
        for disc in overheat_warnings:
            print(f"\n🔥 {disc.get('corp_name', '')} ({disc.get('stock_code', '')})")
            print(f"   {disc.get('report_nm', '')}")
            print(f"   링크: https://dart.fss.or.kr/dsaf001/main.do?rcpNo={disc.get('rcept_no', '')}")
    else:
        print("단기과열종목 예고가 없습니다.")

    # 5. 특정 기업 공시 조회
    print("\n[테스트 5: 특정 기업 공시]")
    # 현대ADM (187660) 예시
    corp_code = dart.get_corp_code('187660')

    if corp_code:
        print(f"현대ADM 기업코드: {corp_code}")

        disclosures = dart.get_disclosures(
            corp_code=corp_code,
            bgn_de='20260201',
            end_de='20260213',
            page_count=10
        )

        if disclosures.get('status') == '000':
            disc_list = disclosures.get('list', [])
            print(f"✅ {len(disc_list)}개 공시 발견")
            for disc in disc_list[:3]:
                print(f"\n• {disc.get('report_nm', '')}")
                print(f"  {disc.get('rcept_dt', '')}")
    else:
        print("기업코드 매핑이 필요합니다.")

    print("\n" + "=" * 60)
    print("✨ 테스트 완료!")
    print("=" * 60)


def test_format():
    """포맷팅 테스트"""
    print("\n[포맷팅 테스트]")

    sample_disclosure = {
        'corp_name': '현대ADM',
        'stock_code': '187660',
        'report_nm': '단기과열종목 지정예고',
        'rcept_dt': '20260213',
        'rcept_no': '20260213000001'
    }

    dart = get_dart()
    formatted = dart.format_disclosure(sample_disclosure)
    print(formatted)


if __name__ == "__main__":
    print("📌 DART API 키가 필요합니다!")
    print("   .env 파일에 DART_API_KEY 설정 확인\n")

    test_dart_service()
    test_format()