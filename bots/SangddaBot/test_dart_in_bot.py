"""
상따봇에서 DART 공시 조회 테스트
"""
import os
import sys

# Argos 루트 경로를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.DartService.dart_service import GetDartData

# 테스트 종목들
test_stocks = [
    ('005930', '삼성전자'),
    ('187660', '현대ADM'),
    ('068790', 'DMS')
]

print("="*60)
print("📢 상따봇 DART 공시 조회 테스트")
print("="*60)

for ticker, name in test_stocks:
    print(f"\n🔍 {name} ({ticker}) 15일치 공시 조회:")
    print("-"*40)

    disclosures = GetDartData(ticker, 15)

    if disclosures:
        print(f"✅ {len(disclosures)}개 공시 발견")
        for i, disc in enumerate(disclosures[:3], 1):  # 최대 3개만 표시
            date_str = disc['date'][4:6] + '/' + disc['date'][6:8] if disc['date'] else ''
            title = disc['title'][:50] + ('...' if len(disc['title']) > 50 else '')
            print(f"  {i}. {date_str} {title}")
    else:
        print("❌ 공시 없음")

print("\n" + "="*60)
print("✨ 테스트 완료")
print("="*60)