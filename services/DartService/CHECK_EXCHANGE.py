"""
거래소 공시 및 기타 공시 확인
"""
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('DART_API_KEY')

print("="*80)
print("🔍 현대ADM 거래소 공시 확인")
print("="*80)

# 1. 단일회사 전체 공시 조회 API
print("\n1️⃣ 단일회사 전체공시 API")
print("-"*40)

url = "https://opendart.fss.or.kr/api/company.json"
params = {
    'crtfc_key': api_key,
    'corp_code': '01409022'
}

response = requests.get(url, params=params, timeout=10)
if response.status_code == 200:
    company = response.json()
    print(f"회사명: {company.get('corp_name', '')}")
    print(f"종목코드: {company.get('stock_code', '')}")
    print(f"상장거래소: {company.get('stock_name', '')}")
else:
    print(f"❌ 회사 정보 조회 실패")

# 2. 공시검색 API로 '단기과열' 키워드 검색
print("\n2️⃣ '단기과열' 키워드 검색")
print("-"*40)

url = "https://opendart.fss.or.kr/api/list.json"

# 2월 1일부터 오늘까지
params = {
    'crtfc_key': api_key,
    'bgn_de': '20260201',
    'end_de': '20260213',
    'page_no': 1,
    'page_count': 100
}

response = requests.get(url, params=params, timeout=10)
result = response.json()

if result.get('status') == '000':
    disclosures = result.get('list', [])
    overheat_found = []

    for disc in disclosures:
        title = disc.get('report_nm', '')
        if '단기과열' in title or '투자주의' in title or '투자경고' in title:
            if disc.get('stock_code') == '187660' or '현대ADM' in disc.get('corp_name', ''):
                overheat_found.append(disc)

    if overheat_found:
        print(f"✅ {len(overheat_found)}개 발견:")
        for disc in overheat_found:
            print(f"   • {disc.get('rcept_dt')}: {disc.get('report_nm', '')}")
            print(f"     회사: {disc.get('corp_name', '')}")
    else:
        print("❌ 관련 공시 없음")

# 3. 거래소 공시는 별도 시스템
print("\n3️⃣ 거래소 공시 안내")
print("-"*40)
print("📌 토스가 보여주는 공시:")
print("   • 단기과열종목 안내")
print("   • 투자주의종목 안내")
print("\n이러한 공시는 한국거래소(KRX) 시스템에서 발행되며,")
print("DART API에는 포함되지 않을 수 있습니다.")
print("\n💡 해결 방안:")
print("1. KRX 정보데이터시스템 API 사용 (별도 신청 필요)")
print("2. DART의 '거래소공시' 카테고리 확인")
print("3. 토스/네이버 등의 공시는 여러 소스를 통합하여 제공")

# 4. 최근 15일 전체 공시 재확인
print("\n4️⃣ 현대ADM 최근 15일 전체 공시")
print("-"*40)

end_date = datetime.now()
start_date = end_date - timedelta(days=14)

params = {
    'crtfc_key': api_key,
    'corp_code': '01409022',
    'bgn_de': start_date.strftime('%Y%m%d'),
    'end_de': end_date.strftime('%Y%m%d'),
    'page_no': 1,
    'page_count': 100
}

response = requests.get(url, params=params, timeout=10)
result = response.json()

if result.get('status') == '000':
    disclosures = result.get('list', [])
    if disclosures:
        print(f"✅ DART API에서 조회 가능한 공시: {len(disclosures)}개")
        for disc in disclosures:
            print(f"   • {disc.get('rcept_dt')}: {disc.get('report_nm', '')}")
    else:
        print("공시 없음")

print("\n" + "="*80)
print("📊 결론:")
print("토스의 '단기과열종목 안내', '투자주의종목 안내'는")
print("한국거래소(KRX) 공시로, DART API에서는 조회되지 않습니다.")
print("="*80)