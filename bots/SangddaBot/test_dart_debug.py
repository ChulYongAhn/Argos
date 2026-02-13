#!/usr/bin/env python
"""DART API 디버그 테스트"""

import os
import sys

# Argos 루트 경로를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.DartService import get_dart
from datetime import datetime, timedelta

def debug_dart():
    """DART API 응답 디버그"""
    print("="*60)
    print("DART API 디버그")
    print("="*60)

    dart = get_dart()

    # 최근 7일간 코스닥 공시 조회
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    print(f"\n📅 조회 기간: {start_date.strftime('%Y%m%d')} ~ {end_date.strftime('%Y%m%d')}")
    print("🔍 코스닥 공시 조회 중...")

    result = dart.get_disclosures(
        bgn_de=start_date.strftime('%Y%m%d'),
        end_de=end_date.strftime('%Y%m%d'),
        corp_cls='K',  # 코스닥
        page_count=100
    )

    print(f"\n📊 API 상태: {result.get('status')}")

    if result.get('status') == '000':
        disclosures = result.get('list', [])
        print(f"✅ 총 {len(disclosures)}개 공시 조회\n")

        # 회사명 목록 출력 (중복 제거)
        companies = {}
        for disc in disclosures:
            corp_name = disc.get('corp_name', '')
            if corp_name and corp_name not in companies:
                companies[corp_name] = disc.get('stock_code', '')

        # 알파벳 순으로 정렬
        sorted_companies = sorted(companies.items())

        print("📋 공시를 낸 회사 목록:")
        for i, (name, code) in enumerate(sorted_companies[:20], 1):
            print(f"  {i:2}. {name} ({code})")

        # "에코프로" 관련 회사 찾기
        print("\n🔍 '에코프로' 관련 회사:")
        eco_found = False
        for name, code in sorted_companies:
            if '에코프로' in name:
                print(f"  ✓ {name} ({code})")
                eco_found = True

        if not eco_found:
            # 정확한 이름 찾기
            print("  ❌ '에코프로'가 포함된 회사명 없음")
            print("\n  비슷한 회사명 검색:")
            for name, code in sorted_companies:
                if '에코' in name or '프로' in name:
                    print(f"    - {name} ({code})")

    else:
        print(f"❌ API 오류: {result.get('message')}")

    print("\n" + "="*60)

if __name__ == "__main__":
    debug_dart()