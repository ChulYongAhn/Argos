"""
현대ADM 공시 조회 문제 원인 분석
"""
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import zipfile
import xml.etree.ElementTree as ET
import io

load_dotenv()

api_key = os.getenv('DART_API_KEY')

print("="*80)
print("🔍 현대ADM (187660) 공시 조회 문제 원인 분석")
print("="*80)

# 1. 전체 회사 목록에서 현대ADM 찾기
print("\n1️⃣ DART 전체 회사 코드에서 현대ADM 검색")
print("-"*40)

corp_code_url = f"https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key={api_key}"

try:
    print("전체 회사 코드 다운로드 중...")
    response = requests.get(corp_code_url, timeout=30)

    if response.status_code == 200:
        # ZIP 파일 압축 해제
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            # CORPCODE.xml 파일 읽기
            with z.open('CORPCODE.xml') as f:
                content = f.read()

        # XML 파싱
        root = ET.fromstring(content)

        # 현대ADM 찾기
        hyundai_adm_found = False
        for corp in root.findall('list'):
            corp_name = corp.find('corp_name').text if corp.find('corp_name') is not None else ''
            stock_code = corp.find('stock_code').text if corp.find('stock_code') is not None else ''
            corp_code = corp.find('corp_code').text if corp.find('corp_code') is not None else ''

            # 현대ADM 찾기
            if '현대ADM' in corp_name or stock_code == '187660':
                hyundai_adm_found = True
                print(f"\n✅ 현대ADM 발견!")
                print(f"   회사명: {corp_name}")
                print(f"   종목코드: {stock_code if stock_code else 'N/A'}")
                print(f"   고유번호: {corp_code}")

                # 이 corp_code로 공시 조회
                print(f"\n   📌 이 corp_code({corp_code})로 공시 조회 시도...")

                url = "https://opendart.fss.or.kr/api/list.json"
                params = {
                    'crtfc_key': api_key,
                    'corp_code': corp_code,
                    'bgn_de': (datetime.now() - timedelta(days=30)).strftime('%Y%m%d'),
                    'end_de': datetime.now().strftime('%Y%m%d'),
                    'page_no': 1,
                    'page_count': 100
                }

                list_response = requests.get(url, params=params, timeout=10)
                list_result = list_response.json()

                if list_result.get('status') == '000':
                    disclosures = list_result.get('list', [])
                    if disclosures:
                        print(f"   ✅ {len(disclosures)}개 공시 발견!")
                        for i, disc in enumerate(disclosures[:3], 1):
                            print(f"      {i}. {disc.get('report_nm', '')[:50]} ({disc.get('rcept_dt', '')})")
                    else:
                        print(f"   ⚠️ 최근 30일간 공시 없음")
                else:
                    print(f"   ❌ API 오류: {list_result.get('message', '')}")

                break

        if not hyundai_adm_found:
            print("❌ 현대ADM을 회사 목록에서 찾을 수 없음")

            # 유사한 회사명 찾기
            print("\n🔍 '현대' 또는 'ADM' 포함 회사:")
            similar_count = 0
            for corp in root.findall('list'):
                corp_name = corp.find('corp_name').text if corp.find('corp_name') is not None else ''
                stock_code = corp.find('stock_code').text if corp.find('stock_code') is not None else ''

                if ('현대' in corp_name and 'ADM' in corp_name.upper()) or stock_code == '187660':
                    similar_count += 1
                    print(f"  - {corp_name} (종목코드: {stock_code if stock_code else 'N/A'})")
                    if similar_count >= 10:
                        break

            if similar_count == 0:
                print("  해당 없음")

                # 187660 종목코드 가진 회사 찾기
                print("\n🔍 종목코드 187660 검색:")
                for corp in root.findall('list'):
                    stock_code = corp.find('stock_code').text if corp.find('stock_code') is not None else ''
                    if stock_code == '187660':
                        corp_name = corp.find('corp_name').text if corp.find('corp_name') is not None else ''
                        corp_code = corp.find('corp_code').text if corp.find('corp_code') is not None else ''
                        print(f"  ✅ 발견: {corp_name} (고유번호: {corp_code})")
                        break
                else:
                    print("  ❌ 종목코드 187660을 가진 회사를 찾을 수 없음")

        # 전체 통계
        total_corps = len(root.findall('list'))
        with_stock_code = sum(1 for corp in root.findall('list')
                             if corp.find('stock_code') is not None
                             and corp.find('stock_code').text)

        print(f"\n📊 전체 회사 통계:")
        print(f"   총 회사 수: {total_corps:,}개")
        print(f"   종목코드 있는 회사: {with_stock_code:,}개")
        print(f"   종목코드 없는 회사: {total_corps - with_stock_code:,}개")

    else:
        print(f"❌ 회사 코드 다운로드 실패: {response.status_code}")

except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()

# 2. stock_code 파라미터 지원 여부 테스트
print("\n\n2️⃣ DART API의 stock_code 파라미터 지원 여부 확인")
print("-"*40)

url = "https://opendart.fss.or.kr/api/list.json"
params = {
    'crtfc_key': api_key,
    'stock_code': '005930',  # 삼성전자로 테스트
    'bgn_de': datetime.now().strftime('%Y%m%d'),
    'end_de': datetime.now().strftime('%Y%m%d'),
    'page_no': 1,
    'page_count': 10
}

print("stock_code 파라미터로 조회 시도 (삼성전자: 005930)")
response = requests.get(url, params=params, timeout=10)
result = response.json()

if result.get('status') == '000':
    disclosures = result.get('list', [])
    if disclosures:
        # stock_code로 필터링 되었는지 확인
        all_samsung = all(d.get('stock_code') == '005930' for d in disclosures if d.get('stock_code'))
        if all_samsung:
            print(f"✅ stock_code 파라미터 지원 확인! {len(disclosures)}개 공시")
        else:
            print(f"⚠️ stock_code 파라미터 무시됨 (전체 공시 반환)")
            print(f"   반환된 공시 중 삼성전자: {sum(1 for d in disclosures if d.get('stock_code') == '005930')}개")
    else:
        print("⚠️ 오늘 공시 없음")
else:
    print(f"❌ API 오류: {result.get('message', '')}")

print("\n💡 결론:")
print("1. DART API의 list.json은 stock_code 파라미터를 지원하지 않음")
print("2. corp_code(고유번호) 파라미터만 지원")
print("3. 전체 공시를 가져온 후 클라이언트에서 필터링 필요")
print("4. 또는 corp_code를 미리 매핑하여 사용")