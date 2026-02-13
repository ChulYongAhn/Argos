"""
2월 12일 공시만 조회
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('DART_API_KEY')
url = "https://opendart.fss.or.kr/api/list.json"

params = {
    'crtfc_key': api_key,
    'bgn_de': '20260212',
    'end_de': '20260212',
    'page_no': 1,
    'page_count': 1689,  # 전체 조회
    'sort': 'date',
    'sort_mth': 'desc'
}

print("2월 12일 공시 조회")
print("="*60)

response = requests.get(url, params=params, timeout=10)
result = response.json()

print(f"API 상태: {result.get('status')} - {result.get('message', '')}")
print(f"총 건수: {result.get('total_count', 0)}\n")

# 현대 관련 찾기
stock_code = "187660"
found = []

if result.get('list'):
    for disc in result['list']:
        corp_name = disc.get('corp_name', '')
        sc = disc.get('stock_code', '')

        if stock_code == sc or 'ADM' in corp_name or '현대ADM' in corp_name:
            found.append(disc)
            print(f"✅ {corp_name} (종목코드: '{sc}')")
            print(f"   제목: {disc.get('report_nm', '')}")
            print(f"   날짜: {disc.get('rcept_dt', '')}\n")

if not found:
    print(f"❌ 종목코드 {stock_code} 또는 '현대ADM' 관련 공시 없음\n")

    # "현대" 포함된 모든 공시 찾기
    print("'현대' 포함된 공시:")
    hyundai_found = []
    for disc in result['list']:
        if '현대' in disc.get('corp_name', ''):
            hyundai_found.append(disc)
            print(f"  - {disc.get('corp_name', '')} ('{disc.get('stock_code', '')}') - {disc.get('report_nm', '')[:50]}")

    if not hyundai_found:
        print("  없음")

    print(f"\n전체 공시 {len(result['list'])}개 중 종목코드 있는 것:")
    with_code = [d for d in result['list'] if d.get('stock_code', '')]
    print(f"  {len(with_code)}개")
    print(f"\n종목코드 없는 것: {len(result['list']) - len(with_code)}개")
