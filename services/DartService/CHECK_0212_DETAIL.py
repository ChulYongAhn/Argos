"""
2월 12일 현대ADM 공시 상세 확인
"""
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('DART_API_KEY')
url = "https://opendart.fss.or.kr/api/list.json"

print("="*80)
print("🔍 2월 12일 현대ADM 공시 확인")
print("="*80)

# 1. 2월 12일만 조회 (corp_code 사용)
print("\n1️⃣ corp_code로 2월 12일 조회")
print("-"*40)

params = {
    'crtfc_key': api_key,
    'corp_code': '01409022',  # 현대ADM
    'bgn_de': '20260212',
    'end_de': '20260212',
    'page_no': 1,
    'page_count': 100
}

response = requests.get(url, params=params, timeout=10)
result = response.json()

if result.get('status') == '000':
    disclosures = result.get('list', [])
    if disclosures:
        print(f"✅ {len(disclosures)}개 공시 발견:")
        for disc in disclosures:
            print(f"   • {disc.get('report_nm', '')}")
            print(f"     접수번호: {disc.get('rcept_no', '')}")
            print(f"     제출인: {disc.get('flr_nm', '')}")
    else:
        print("❌ 2월 12일 공시 없음")
else:
    print(f"❌ API 오류: {result.get('message', '')}")

# 2. 2월 11일~13일 조회 (더 넓은 범위)
print("\n2️⃣ 2월 11일~13일 전체 조회")
print("-"*40)

params = {
    'crtfc_key': api_key,
    'corp_code': '01409022',
    'bgn_de': '20260211',
    'end_de': '20260213',
    'page_no': 1,
    'page_count': 100
}

response = requests.get(url, params=params, timeout=10)
result = response.json()

if result.get('status') == '000':
    disclosures = result.get('list', [])
    if disclosures:
        print(f"✅ {len(disclosures)}개 공시:")
        for disc in disclosures:
            date = disc.get('rcept_dt', '')
            print(f"   • {date}: {disc.get('report_nm', '')}")
    else:
        print("공시 없음")

# 3. 2월 12일 전체 공시에서 현대ADM 찾기
print("\n3️⃣ 2월 12일 전체 공시에서 현대ADM 검색")
print("-"*40)

params = {
    'crtfc_key': api_key,
    'bgn_de': '20260212',
    'end_de': '20260212',
    'page_no': 1,
    'page_count': 100,
    'pblntf_ty': 'B'  # 정기공시
}

response = requests.get(url, params=params, timeout=10)
result = response.json()

hyundai_found = []
if result.get('status') == '000':
    for disc in result.get('list', []):
        if '현대ADM' in disc.get('corp_name', ''):
            hyundai_found.append(disc)

if hyundai_found:
    print(f"✅ 정기공시에서 {len(hyundai_found)}개 발견:")
    for disc in hyundai_found:
        print(f"   • {disc.get('report_nm', '')}")
else:
    print("❌ 정기공시에서 현대ADM 없음")

# 4. 다른 공시 유형 확인
print("\n4️⃣ 다른 공시 유형별 조회")
print("-"*40)

pblntf_types = [
    ('A', '정기공시'),
    ('B', '주요사항보고'),
    ('C', '발행공시'),
    ('D', '지분공시'),
    ('E', '기타공시'),
    ('F', '외부감사관련'),
    ('G', '펀드공시'),
    ('H', '자산유동화'),
    ('I', '거래소공시'),
    ('J', '공정위공시')
]

for pblntf_ty, name in pblntf_types:
    params = {
        'crtfc_key': api_key,
        'corp_code': '01409022',
        'bgn_de': '20260212',
        'end_de': '20260212',
        'pblntf_ty': pblntf_ty,
        'page_no': 1,
        'page_count': 10
    }

    response = requests.get(url, params=params, timeout=10)
    result = response.json()

    if result.get('status') == '000' and result.get('list'):
        print(f"✅ {name}({pblntf_ty}): {len(result.get('list'))}개")
        for disc in result.get('list', []):
            print(f"     • {disc.get('report_nm', '')}")