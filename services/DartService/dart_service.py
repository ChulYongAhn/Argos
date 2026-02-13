"""
DART 전자공시 서비스
- 종목코드로 공시 조회
"""

import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import zipfile
import xml.etree.ElementTree as ET
import io

# .env 파일 로드
load_dotenv()


class _DartService:
    """DART OpenAPI 서비스 (내부 클래스)"""

    def __init__(self):
        """초기화"""
        self.api_key = os.getenv('DART_API_KEY')
        if not self.api_key:
            raise ValueError("DART_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
        self.base_url = "https://opendart.fss.or.kr/api"
        self._corp_code_map = None  # 종목코드 -> 고유번호 매핑 캐시

    def _load_corp_codes(self) -> Dict[str, str]:
        """전체 회사 코드 매핑 로드 (종목코드 -> 고유번호)"""
        if self._corp_code_map is not None:
            return self._corp_code_map

        self._corp_code_map = {}

        try:
            print("📥 회사 코드 매핑 로드 중...")
            url = f"{self.base_url}/corpCode.xml?crtfc_key={self.api_key}"
            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                # ZIP 파일 압축 해제
                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    with z.open('CORPCODE.xml') as f:
                        content = f.read()

                # XML 파싱
                root = ET.fromstring(content)

                # 종목코드 -> 고유번호 매핑
                for corp in root.findall('list'):
                    stock_code = corp.find('stock_code').text if corp.find('stock_code') is not None else ''
                    corp_code = corp.find('corp_code').text if corp.find('corp_code') is not None else ''
                    corp_name = corp.find('corp_name').text if corp.find('corp_name') is not None else ''

                    if stock_code and corp_code:
                        self._corp_code_map[stock_code] = {
                            'corp_code': corp_code,
                            'corp_name': corp_name
                        }

                print(f"✅ {len(self._corp_code_map):,}개 회사 코드 매핑 완료")
            else:
                print(f"⚠️ 회사 코드 로드 실패: {response.status_code}")

        except Exception as e:
            print(f"⚠️ 회사 코드 로드 오류: {e}")

        return self._corp_code_map

    def _get_corp_code(self, stock_code: str) -> Optional[str]:
        """종목코드로 고유번호 조회"""
        corp_map = self._load_corp_codes()
        corp_info = corp_map.get(stock_code)
        if corp_info:
            print(f"📌 {corp_info['corp_name']} ({stock_code}) -> corp_code: {corp_info['corp_code']}")
            return corp_info['corp_code']
        return None

    def _get_disclosures_by_stock(
        self,
        stock_code: str,
        bgn_de: str,
        end_de: str
    ) -> List[Dict[str, Any]]:
        """
        종목코드로 공시 조회 (corp_code 사용)

        Args:
            stock_code: 종목코드 (예: '005930')
            bgn_de: 시작일 (YYYYMMDD)
            end_de: 종료일 (YYYYMMDD)

        Returns:
            공시 목록
        """
        # 종목코드를 고유번호로 변환
        corp_code = self._get_corp_code(stock_code)
        if not corp_code:
            print(f"⚠️ 종목코드 {stock_code}에 대한 회사 정보를 찾을 수 없습니다.")
            return []

        url = f"{self.base_url}/list.json"
        filtered = []

        try:
            params = {
                'crtfc_key': self.api_key,
                'corp_code': corp_code,  # corp_code 사용
                'bgn_de': bgn_de,
                'end_de': end_de,
                'page_no': 1,
                'page_count': 100,
                'sort': 'date',
                'sort_mth': 'desc'
            }

            print(f"\n{'='*60}")
            print(f"📡 DART API 공시 조회")
            print(f"종목코드: {stock_code} -> 고유번호: {corp_code}")
            print(f"조회 기간: {bgn_de} ~ {end_de}")
            print(f"{'='*60}\n")

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            result = response.json()

            if result.get('status') != '000':
                print(f"⚠️ DART API 상태: {result.get('status')} - {result.get('message', '')}")
                return []

            all_disclosures = result.get('list', [])

            if not all_disclosures:
                print(f"⚠️ 해당 기간에 공시가 없습니다.")
                return []

            print(f"✅ {len(all_disclosures)}개 공시 발견")

            # 공시 정보 변환
            for disc in all_disclosures:
                filtered.append({
                    'date': disc.get('rcept_dt', ''),
                    'title': disc.get('report_nm', ''),
                    'link': f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={disc.get('rcept_no', '')}"
                })

            return filtered

        except Exception as e:
            print(f"❌ DART API 오류: {e}")
            import traceback
            traceback.print_exc()
            return []


# 싱글톤 인스턴스
_dart_instance = None


def _get_dart() -> _DartService:
    """DART 서비스 싱글톤 인스턴스 반환"""
    global _dart_instance
    if _dart_instance is None:
        _dart_instance = _DartService()
    return _dart_instance


def GetDartData(stock_code: str, days: int = 7) -> List[Dict[str, Any]]:
    """
    종목코드로 공시 조회 (오늘 포함 N일치)

    Args:
        stock_code: 종목코드 (예: '005930')
        days: 조회 기간 (오늘 포함, 기본 7일)

    Returns:
        공시 목록 (date, title, link)

    Example:
        GetDartData("005930", 7)  # 삼성전자 7일치 공시
    """
    if not stock_code:
        print("❌ 종목코드가 필요합니다.")
        return []

    try:
        # 날짜 계산
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days-1)

        # 공시 조회
        dart = _get_dart()
        return dart._get_disclosures_by_stock(
            stock_code=stock_code,
            bgn_de=start_date.strftime('%Y%m%d'),
            end_de=end_date.strftime('%Y%m%d')
        )

    except Exception as e:
        print(f"❌ GetDartData 오류: {e}")
        return []