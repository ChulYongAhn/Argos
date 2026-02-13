#!/usr/bin/env python
"""현대ADM 공시 조회 테스트"""

import os
import sys

# Argos 루트 경로를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.DartService import get_dart
from datetime import datetime, timedelta

def find_hyundai_adm():
    """현대ADM(187660) 공시 찾기"""
    print("="*60)
    print("현대ADM(187660) 공시 조회")
    print("="*60)

    dart = get_dart()

    # 최근 60일간 코스닥 공시 조회
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)

    print(f"\n📅 조회 기간: {start_date.strftime('%Y%m%d')} ~ {end_date.strftime('%Y%m%d')}")
    print("🔍 코스닥 전체 공시 조회 중...")

    # 여러 페이지 조회 (페이지당 100개)
    all_disclosures = []
    for page in range(1, 6):  # 1~5 페이지 (500개)
        result = dart.get_disclosures(
            bgn_de=start_date.strftime('%Y%m%d'),
            end_de=end_date.strftime('%Y%m%d'),
            corp_cls='K',  # 코스닥
            page_no=page,
            page_count=100
        )
        if result.get('status') == '000':
            all_disclosures.extend(result.get('list', []))
            print(f"  페이지 {page}: {len(result.get('list', []))}개")
        else:
            break

    if all_disclosures:
        print(f"✅ 총 {len(all_disclosures)}개 공시 조회\n")

        # 현대ADM 찾기 - 종목코드와 회사명으로 검색
        print("🔍 현대ADM 공시 검색:")
        hyundai_disclosures = []

        for disc in all_disclosures:
            stock_code = disc.get('stock_code', '')
            corp_name = disc.get('corp_name', '')

            # 종목코드 187660 또는 회사명에 '현대' 포함
            if stock_code == '187660' or '현대' in corp_name:
                hyundai_disclosures.append(disc)
                print(f"\n  ✓ 발견!")
                print(f"    회사명: {corp_name}")
                print(f"    종목코드: {stock_code}")
                print(f"    공시일: {disc.get('rcept_dt', '')}")
                print(f"    제목: {disc.get('report_nm', '')}")
                print(f"    링크: https://dart.fss.or.kr/dsaf001/main.do?rcpNo={disc.get('rcept_no', '')}")

        if not hyundai_disclosures:
            print("\n  ❌ 현대ADM 공시를 찾지 못했습니다.")
            print("\n  📋 최근 공시 회사 목록 (처음 20개):")
            for i, disc in enumerate(all_disclosures[:20], 1):
                print(f"    {i:2}. {disc.get('corp_name')} ({disc.get('stock_code')})")

    else:
        print(f"❌ API 오류: {result.get('message')}")

    print("\n" + "="*60)

if __name__ == "__main__":
    find_hyundai_adm()