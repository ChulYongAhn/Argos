#!/usr/bin/env python3
"""DART 공시 조회 테스트"""

import os
import sys
from datetime import datetime, timedelta

# 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

# .env 로드
from dotenv import load_dotenv
load_dotenv()

from services.DartService import get_dart

print("=" * 60)
print("DART 공시 조회 테스트")
print("=" * 60)

# DART 서비스 가져오기
dart = get_dart()

# 테스트할 회사명
corp_name = "현대에이디엠"  # 현대ADM의 정식 회사명

# 날짜 설정
end_date = datetime.now().strftime('%Y%m%d')
start_date = (datetime.now() - timedelta(days=15)).strftime('%Y%m%d')

print(f"\n회사명: {corp_name}")
print(f"조회 기간: {start_date} ~ {end_date}")

# 전체 공시 조회
print(f"\n1. 전체 공시 조회 중...")
all_disclosures = dart.get_disclosures(
    bgn_de=start_date,
    end_de=end_date,
    page_count=100
)

if all_disclosures and all_disclosures.get('status') == '000':
    total_count = len(all_disclosures.get('list', []))
    print(f"   ✓ 전체 공시: {total_count}개")

    # 처음 5개 공시의 회사명 출력
    print("\n   최근 5개 공시 회사명:")
    for i, disc in enumerate(all_disclosures.get('list', [])[:5]):
        print(f"   {i+1}. {disc.get('corp_name')} - {disc.get('report_nm', '')[:30]}")

    # 현대ADM 관련 공시 찾기
    print(f"\n2. '{corp_name}' 관련 공시 검색 중...")
    found_disclosures = []

    # 다양한 매칭 시도
    test_names = ["현대에이디엠", "현대ADM", "현대", "에이디엠", "ADM"]

    for test_name in test_names:
        print(f"\n   '{test_name}'로 검색:")
        for disc in all_disclosures.get('list', []):
            disc_corp_name = disc.get('corp_name', '')
            if test_name in disc_corp_name or disc_corp_name in test_name:
                print(f"      ✓ 발견: {disc_corp_name} - {disc.get('report_nm', '')[:30]}")
                found_disclosures.append(disc)
                break

    if found_disclosures:
        print(f"\n3. 발견된 공시 상세:")
        for disc in found_disclosures[:5]:
            print(f"\n   회사명: {disc.get('corp_name')}")
            print(f"   날짜: {disc.get('rcept_dt')}")
            print(f"   제목: {disc.get('report_nm')}")
            rcept_no = disc.get('rcept_no', '')
            if rcept_no:
                link = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}"
                print(f"   링크: {link}")
    else:
        print("\n   ⚠️ 해당 회사의 공시를 찾지 못했습니다.")

else:
    print("   ✗ DART API 응답 오류")
    print(f"   상태 코드: {all_disclosures.get('status') if all_disclosures else 'None'}")
    print(f"   메시지: {all_disclosures.get('message') if all_disclosures else 'None'}")

print("\n" + "=" * 60)