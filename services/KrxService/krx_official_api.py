"""
KRX 공식 API를 사용한 과거 공시 조회
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json

def get_krx_announcements(stock_code: str, days: int = 15) -> List[Dict[str, Any]]:
    """
    KRX 공식 API로 과거 공시 조회 시도

    Args:
        stock_code: 종목코드
        days: 조회 기간

    Returns:
        공시 리스트
    """

    announcements = []

    # 1. KRX 투자주의/경고 종목 이력 조회
    print(f"\n🔍 KRX API로 {stock_code} 과거 {days}일 공시 조회 시도...")

    try:
        # KRX data.krx.co.kr API endpoint
        base_url = "http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # 1) 투자주의종목 조회
        params = {
            'bld': 'dbms/MDC/STAT/standard/MDCSTAT04301',  # 투자주의종목
            'isuCd': stock_code,
            'strtDd': start_date.strftime('%Y%m%d'),
            'endDd': end_date.strftime('%Y%m%d')
        }

        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'http://data.krx.co.kr'
        }

        response = requests.post(base_url, data=params, headers=headers, timeout=10)

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"응답: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")

                # 데이터 파싱
                if 'block1' in data:
                    for item in data['block1']:
                        announcements.append({
                            'date': item.get('TRD_DD', ''),
                            'title': f"투자주의종목 - {item.get('ISU_NM', '')}",
                            'type': 'KRX'
                        })
            except:
                print("JSON 파싱 실패")
        else:
            print(f"상태코드: {response.status_code}")

        # 2) 단기과열종목 조회
        params['bld'] = 'dbms/MDC/STAT/standard/MDCSTAT03901'  # 단기과열

        response = requests.post(base_url, data=params, headers=headers, timeout=10)

        if response.status_code == 200:
            try:
                data = response.json()
                if 'block1' in data:
                    for item in data['block1']:
                        announcements.append({
                            'date': item.get('DSGT_DD', ''),
                            'title': '단기과열종목 지정',
                            'type': 'KRX'
                        })
            except:
                pass

        # 3) 관리종목 조회
        params['bld'] = 'dbms/MDC/STAT/standard/MDCSTAT04501'  # 관리종목

        response = requests.post(base_url, data=params, headers=headers, timeout=10)

        if response.status_code == 200:
            try:
                data = response.json()
                if 'block1' in data:
                    for item in data['block1']:
                        announcements.append({
                            'date': item.get('DSGT_DD', ''),
                            'title': '관리종목 지정',
                            'type': 'KRX'
                        })
            except:
                pass

    except Exception as e:
        print(f"❌ KRX API 오류: {e}")

    # 4. KIND (한국거래소 공시) 시스템 확인
    print(f"\n🔍 KIND 시스템 공시 조회...")

    try:
        # KIND는 별도 시스템으로 공시 제공
        kind_url = "http://kind.krx.co.kr/common/searchcorpname.do"

        params = {
            'method': 'searchCorpNameJson',
            'searchCodeType': '13',
            'searchCorpName': stock_code,
            'marketType': '',
            'currentPageSize': '5000'
        }

        response = requests.get(kind_url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                corp_code = data[0].get('repIsuSrtCd', '')

                # 공시 목록 조회
                disclosure_url = "http://kind.krx.co.kr/disclosure/searchtotalinfo.do"

                params = {
                    'method': 'searchTotalInfoSub',
                    'forward': 'searchtotalinfo_detail',
                    'searchCodeType': 'W',
                    'searchCorpName': stock_code,
                    'startDate': start_date.strftime('%Y%m%d'),
                    'endDate': end_date.strftime('%Y%m%d'),
                    'pageIndex': '1'
                }

                # KIND는 HTML 반환이므로 파싱 필요
                print("KIND는 HTML 반환 - BeautifulSoup 필요")

    except Exception as e:
        print(f"❌ KIND 조회 오류: {e}")

    return announcements


# 테스트
if __name__ == "__main__":
    print("="*80)
    print("🔍 KRX 공식 API 과거 공시 조회 테스트")
    print("="*80)

    test_stocks = [
        ('187660', '현대ADM'),
        ('005930', '삼성전자')
    ]

    for stock_code, name in test_stocks:
        print(f"\n📊 {name} ({stock_code})")
        print("-"*40)

        announcements = get_krx_announcements(stock_code, 15)

        if announcements:
            print(f"\n✅ {len(announcements)}개 공시 발견:")
            for ann in announcements:
                print(f"  • {ann['date']}: {ann['title']}")
        else:
            print("\n❌ 과거 공시 조회 실패 또는 없음")

    print("\n" + "="*80)
    print("💡 결론:")
    print("1. KRX data.krx.co.kr는 현재 상태 위주 제공")
    print("2. 과거 이력은 제한적 (일부 통계만)")
    print("3. KIND 시스템은 HTML 파싱 필요")
    print("4. DART와 달리 체계적인 과거 공시 API 부재")
    print("="*80)