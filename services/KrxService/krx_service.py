"""
KRX(한국거래소) 공시 서비스
- 단기과열종목, 투자주의종목 등 거래소 공시 조회
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

class KrxService:
    """KRX 공시 조회 서비스"""

    def __init__(self):
        """초기화"""
        # KRX는 공개 API를 제공하지만 인증키는 필요없음
        self.base_url = "http://data.krx.co.kr"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://data.krx.co.kr'
        }

    def get_overheat_stocks(self, market: str = "KOSDAQ") -> List[Dict[str, Any]]:
        """
        단기과열종목 조회

        Args:
            market: 시장구분 (KOSDAQ, KOSPI)

        Returns:
            단기과열종목 리스트
        """
        try:
            # KRX 데이터 API 엔드포인트
            url = f"{self.base_url}/comm/bldAttendant/getJsonData.cmd"

            # 오늘 날짜
            today = datetime.now().strftime("%Y%m%d")

            params = {
                'bld': 'dbms/MDC/STAT/standard/MDCSTAT03901',
                'mktId': 'KSQ' if market == 'KOSDAQ' else 'STK',
                'trdDd': today
            }

            response = requests.get(url, params=params, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return self._parse_overheat_data(data)
            else:
                print(f"❌ KRX API 응답 오류: {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ KRX 단기과열 조회 오류: {e}")
            return []

    def get_investment_warning(self, stock_code: str) -> Dict[str, Any]:
        """
        특정 종목의 투자주의/경고 정보 조회

        Args:
            stock_code: 종목코드

        Returns:
            투자주의 정보
        """
        try:
            url = f"{self.base_url}/comm/bldAttendant/getJsonData.cmd"

            params = {
                'bld': 'dbms/MDC/STAT/standard/MDCSTAT04301',
                'isuCd': stock_code
            }

            response = requests.get(url, params=params, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return self._parse_warning_data(data)
            else:
                return {}

        except Exception as e:
            print(f"❌ KRX 투자주의 조회 오류: {e}")
            return {}

    def _parse_overheat_data(self, data: Dict) -> List[Dict[str, Any]]:
        """단기과열 데이터 파싱"""
        results = []

        if 'block1' in data:
            for item in data['block1']:
                results.append({
                    'stock_code': item.get('ISU_SRT_CD', ''),
                    'stock_name': item.get('ISU_NM', ''),
                    'designation_date': item.get('DSGT_DD', ''),
                    'type': '단기과열종목'
                })

        return results

    def _parse_warning_data(self, data: Dict) -> Dict[str, Any]:
        """투자주의 데이터 파싱"""
        if 'block1' in data and len(data['block1']) > 0:
            item = data['block1'][0]
            return {
                'status': item.get('INVT_ALRM_CLS_NM', ''),
                'designation_date': item.get('DSGT_DD', ''),
                'reason': item.get('DSGT_RSN', '')
            }
        return {}


def GetKrxDisclosures(stock_code: str, days: int = 15) -> List[Dict[str, Any]]:
    """
    KRX 거래소 공시 조회 (간편 함수)

    Args:
        stock_code: 종목코드
        days: 조회 기간 (현재는 최신 정보만 제공)

    Returns:
        거래소 공시 리스트
    """
    krx = KrxService()
    disclosures = []

    # 1. 단기과열종목 확인
    overheat_stocks = krx.get_overheat_stocks()
    for stock in overheat_stocks:
        if stock['stock_code'] == stock_code:
            disclosures.append({
                'date': stock['designation_date'],
                'title': '단기과열종목 지정',
                'type': 'KRX'
            })

    # 2. 투자주의/경고 확인
    warning_info = krx.get_investment_warning(stock_code)
    if warning_info:
        disclosures.append({
            'date': warning_info.get('designation_date', ''),
            'title': f"투자{warning_info.get('status', '주의')} 지정",
            'type': 'KRX'
        })

    return disclosures


# 대안: 웹 스크래핑 방식 (KRX API가 안될 경우)
def scrape_krx_disclosures(stock_code: str) -> List[Dict[str, Any]]:
    """
    KRX 웹사이트에서 공시 스크래핑 (백업 방법)

    Note:
        KRX는 robots.txt로 크롤링을 제한할 수 있으므로
        공식 API 사용을 권장합니다.
    """
    try:
        # KRX 공시 페이지 URL
        url = f"http://kind.krx.co.kr/disclosure/searchtotalinfo.do"

        params = {
            'method': 'searchTotalInfoSub',
            'forward': 'searchtotalinfo_detail',
            'searchCodeType': 'W',
            'searchCorpName': stock_code,
            'pageIndex': '1'
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code == 200:
            # HTML 파싱 (BeautifulSoup 필요)
            # 여기서는 간단한 예시만 제공
            print("📌 웹 스크래핑은 BeautifulSoup 라이브러리가 필요합니다.")
            return []
        else:
            return []

    except Exception as e:
        print(f"❌ KRX 스크래핑 오류: {e}")
        return []


if __name__ == "__main__":
    """테스트"""
    print("=" * 60)
    print("🔍 KRX 공시 서비스 테스트")
    print("=" * 60)

    # 현대ADM 테스트
    stock_code = "187660"
    print(f"\n종목: 현대ADM ({stock_code})")
    print("-" * 40)

    disclosures = GetKrxDisclosures(stock_code)

    if disclosures:
        print(f"✅ {len(disclosures)}개 KRX 공시:")
        for disc in disclosures:
            print(f"  • {disc['date']}: {disc['title']}")
    else:
        print("❌ KRX 공시 없음 (또는 조회 실패)")

    print("\n📌 참고:")
    print("1. KRX API는 실시간 데이터를 제공합니다.")
    print("2. 일부 기능은 추가 개발이 필요할 수 있습니다.")
    print("3. 상용 서비스는 KRX 정보데이터시스템 정식 API 신청을 권장합니다.")