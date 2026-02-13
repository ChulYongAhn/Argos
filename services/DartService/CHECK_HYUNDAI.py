"""
현대ADM 공시 직접 확인 - 상세 디버깅 버전
"""
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json

load_dotenv()

api_key = os.getenv('DART_API_KEY')
url = "https://opendart.fss.or.kr/api/list.json"

# 최근 15일
end_date = datetime.now()
start_date = end_date - timedelta(days=14)

params = {
    'crtfc_key': api_key,
    'bgn_de': start_date.strftime('%Y%m%d'),
    'end_de': end_date.strftime('%Y%m%d'),
    'page_no': 1,
    'page_count': 100,
    'sort': 'date',
    'sort_mth': 'desc'
}

print("="*80)
print("🔍 현대ADM 공시 조회 상세 디버깅")
print("="*80)
print(f"조회 기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
print(f"대상 종목: 현대ADM (종목코드: 187660)")
print("="*80)

# 현대ADM 찾기
target_stock_code = "187660"
found_by_code = []
found_by_name = []
all_stock_codes = set()
all_corp_names = {}

# 10페이지까지 조회
for page in range(1, 11):
    params['page_no'] = page
    response = requests.get(url, params=params, timeout=10)
    result = response.json()

    if page == 1:
        print(f"\n📡 API 응답 정보:")
        print(f"  - 상태: {result.get('status')} - {result.get('message', 'OK')}")
        print(f"  - 총 건수: {result.get('total_count', 0):,}개")
        print(f"  - 총 페이지: {result.get('total_page', 0)}페이지")
        print("-"*80)

    if result.get('status') != '000':
        print(f"❌ API 오류: {result.get('status')} - {result.get('message', '')}")
        break

    if not result.get('list'):
        print(f"페이지 {page}: 데이터 없음")
        break

    disclosures = result['list']
    print(f"\n📄 페이지 {page}: {len(disclosures)}개 공시")

    for i, disc in enumerate(disclosures):
        corp_name = disc.get('corp_name', '')
        stock_code = disc.get('stock_code', '')

        # 모든 종목코드 수집
        if stock_code:
            all_stock_codes.add(stock_code)
            all_corp_names[stock_code] = corp_name

        # 종목코드로 매칭
        if stock_code == target_stock_code:
            found_by_code.append(disc)
            print(f"\n  ✅ 종목코드 매칭! (인덱스: {i})")
            print(f"     회사명: {corp_name}")
            print(f"     종목코드: [{stock_code}]")
            print(f"     공시제목: {disc.get('report_nm', '')}")
            print(f"     접수일: {disc.get('rcept_dt', '')}")
            print(f"     고유번호: {disc.get('corp_code', '')}")

        # 회사명으로 매칭
        if '현대' in corp_name and ('ADM' in corp_name or 'adm' in corp_name.lower()):
            found_by_name.append(disc)
            if stock_code != target_stock_code:  # 종목코드가 다른 경우만 출력
                print(f"\n  ⚠️ 회사명 매칭! (종목코드 불일치) (인덱스: {i})")
                print(f"     회사명: {corp_name}")
                print(f"     종목코드: [{stock_code}] (기대값: {target_stock_code})")
                print(f"     공시제목: {disc.get('report_nm', '')}")
                print(f"     접수일: {disc.get('rcept_dt', '')}")

    # 첫 페이지에서 샘플 데이터 출력
    if page == 1:
        print("\n  📋 첫 페이지 샘플 (처음 5개):")
        for i, disc in enumerate(disclosures[:5]):
            sc = disc.get('stock_code', 'N/A')
            cn = disc.get('corp_name', '')
            print(f"    {i+1}. [{sc:>8}] {cn[:30]:<30}")

    if len(found_by_code) >= 3:
        print("\n  ✅ 충분한 공시를 찾아 조회 종료")
        break

# 결과 요약
print("\n" + "="*80)
print("📊 조회 결과 요약")
print("="*80)

if found_by_code:
    print(f"✅ 종목코드 {target_stock_code}로 찾은 공시: {len(found_by_code)}개")
    for i, disc in enumerate(found_by_code[:3], 1):
        print(f"  {i}. {disc.get('report_nm', '')[:50]} ({disc.get('rcept_dt', '')})")
else:
    print(f"❌ 종목코드 {target_stock_code}로 공시를 찾지 못했습니다.")

if found_by_name and not found_by_code:
    print(f"\n⚠️ '현대ADM' 이름으로 찾은 공시: {len(found_by_name)}개")
    for disc in found_by_name[:3]:
        print(f"  - {disc.get('corp_name', '')} [{disc.get('stock_code', 'N/A')}]")
        print(f"    {disc.get('report_nm', '')[:50]} ({disc.get('rcept_dt', '')})")

# 종목코드 통계
print(f"\n📈 종목코드 통계:")
print(f"  - 조회된 고유 종목코드 수: {len(all_stock_codes)}개")
print(f"  - 187660이 포함되어 있는가? {'예' if target_stock_code in all_stock_codes else '아니오'}")

# 유사한 종목 찾기
if not found_by_code:
    print(f"\n🔍 '현대' 관련 종목:")
    for code, name in all_corp_names.items():
        if '현대' in name:
            print(f"  - [{code}] {name}")
            if len([c for c, n in all_corp_names.items() if '현대' in n]) >= 5:
                print("  ... (더 많은 항목 생략)")
                break
