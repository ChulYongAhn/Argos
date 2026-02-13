#!/usr/bin/env python
"""개선된 공시 조회 테스트"""

import os
import sys

# Argos 루트 경로를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Starter import SangddaBot

def test_improved_disclosure():
    """개선된 공시 조회 테스트"""
    print("="*60)
    print("개선된 공시 조회 테스트")
    print("="*60)

    bot = SangddaBot()

    # 테스트 케이스
    test_cases = [
        ("현대ADM", "187660"),
        ("에코프로", "086520"),
        ("알테오젠", "196170"),
        ("현대무벡스", "319400")
    ]

    for name, ticker in test_cases:
        print(f"\n📋 {name}({ticker}) 공시 조회:")
        disclosures = bot.get_recent_disclosures(name, ticker=ticker, days=30)

        if disclosures:
            for disc in disclosures:
                print(f"  - [{disc['date']}] {disc['title'][:40]}")
        else:
            print(f"  공시 없음")

    print("\n" + "="*60)

if __name__ == "__main__":
    test_improved_disclosure()