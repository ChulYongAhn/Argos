"""
현대ADM 날짜별 공시 확인
"""
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('DART_API_KEY')
url = "https://opendart.fss.or.kr/api/list.json"

# 현대ADM corp_code
corp_code = '01409022'

print("="*80)
print("🔍 현대ADM 날짜별 공시 확인")
print("="*80)

# 여러 기간으로 테스트
test_periods = [
    (7, "7일"),
    (15, "15일"),
    (30, "30일"),
    (60, "60일")
]

for days, label in test_periods:
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days-1)  # 오늘 포함

    params = {
        'crtfc_key': api_key,
        'corp_code': corp_code,
        'bgn_de': start_date.strftime('%Y%m%d'),
        'end_de': end_date.strftime('%Y%m%d'),
        'page_no': 1,
        'page_count': 100
    }

    print(f"\n📅 최근 {label} ({start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')})")
    print("-"*40)

    response = requests.get(url, params=params, timeout=10)
    result = response.json()

    if result.get('status') == '000':
        disclosures = result.get('list', [])
        if disclosures:
            print(f"✅ {len(disclosures)}개 공시 발견:")
            for disc in disclosures:
                date = disc.get('rcept_dt', '')
                title = disc.get('report_nm', '')
                formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:8]}" if date else ''
                print(f"   • {formatted_date}: {title[:60]}")
        else:
            print("   공시 없음")
    else:
        print(f"❌ API 오류: {result.get('message', '')}")

# GetDartData 함수 직접 테스트
print("\n" + "="*80)
print("📊 GetDartData 함수 테스트")
print("="*80)

from services.DartService.dart_service import GetDartData

for days, label in [(15, "15일"), (30, "30일")]:
    print(f"\n📅 GetDartData('187660', {days})")
    print("-"*40)

    disclosures = GetDartData('187660', days)

    if disclosures:
        print(f"✅ {len(disclosures)}개 공시:")
        for disc in disclosures:
            date = disc.get('date', '')
            title = disc.get('title', '')
            formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:8]}" if date else ''
            print(f"   • {formatted_date}: {title[:60]}")
    else:
        print("   공시 없음")