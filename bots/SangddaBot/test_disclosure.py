#!/usr/bin/env python
"""공시 조회 기능 테스트"""

import os
import sys

# Argos 루트 경로를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Starter import SangddaBot
from datetime import datetime

def test_disclosure():
    """특정 기업의 공시 조회 테스트"""
    print("="*60)
    print("공시 조회 테스트")
    print("="*60)

    bot = SangddaBot()

    # 테스트할 회사들 (코스닥 상위 기업)
    test_companies = [
        "에코프로",
        "알테오젠",
        "에코프로비엠",
        "레인보우로보틱스",
        "삼천당제약"
    ]

    for company in test_companies:
        print(f"\n📋 {company} 공시 조회:")
        disclosures = bot.get_recent_disclosures(company, days=30)

        if disclosures:
            for disc in disclosures:
                print(f"  - [{disc['date']}] {disc['title'][:50]}")
                print(f"    {disc['link']}")
        else:
            print(f"  공시 없음")

    print("\n" + "="*60)

if __name__ == "__main__":
    test_disclosure()