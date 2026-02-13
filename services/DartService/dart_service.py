"""
DART 전자공시 서비스
- 공시 조회, 재무제표 조회, 기업 정보 조회
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


class DartService:
    """DART OpenAPI 서비스"""

    def __init__(self, api_key: Optional[str] = None):
        """
        초기화

        Args:
            api_key: DART API 키 (없으면 환경변수에서 로드)
        """
        self.api_key = api_key or os.getenv('DART_API_KEY')
        if not self.api_key:
            raise ValueError("DART_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")

        self.base_url = "https://opendart.fss.or.kr/api"

    def get_corp_code(self, stock_code: str) -> Optional[str]:
        """
        종목코드로 기업코드 조회

        Args:
            stock_code: 종목코드 (예: '005930')

        Returns:
            기업코드 또는 None
        """
        # 고유번호 다운로드 및 매핑 필요
        # 실제 구현에서는 corpCode.xml을 파싱해야 함
        # 여기서는 간단한 매핑 예시
        corp_mapping = {
            '187660': '00187660',  # 현대ADM 예시
            '005930': '00126380',  # 삼성전자 예시
        }
        return corp_mapping.get(stock_code)

    def get_disclosures(
        self,
        corp_code: Optional[str] = None,
        bgn_de: Optional[str] = None,
        end_de: Optional[str] = None,
        last_reprt_at: str = 'N',
        pblntf_ty: Optional[str] = None,
        pblntf_detail_ty: Optional[str] = None,
        corp_cls: Optional[str] = None,
        sort: str = 'date',
        sort_mth: str = 'desc',
        page_no: int = 1,
        page_count: int = 10
    ) -> Dict[str, Any]:
        """
        공시 검색

        Args:
            corp_code: 기업코드
            bgn_de: 시작일 (YYYYMMDD)
            end_de: 종료일 (YYYYMMDD)
            last_reprt_at: 최종보고서 여부
            pblntf_ty: 공시유형 (A:정기공시, B:주요사항보고, C:발행공시, D:지분공시 등)
            pblntf_detail_ty: 공시상세유형
            corp_cls: 법인구분 (Y:유가증권, K:코스닥, N:코넥스, E:기타)
            sort: 정렬 (date:날짜, crp:회사명, rpt:보고서명)
            sort_mth: 정렬방법 (asc:오름차순, desc:내림차순)
            page_no: 페이지 번호
            page_count: 페이지당 건수

        Returns:
            공시 목록
        """
        url = f"{self.base_url}/list.json"

        params = {
            'crtfc_key': self.api_key,
            'page_no': page_no,
            'page_count': page_count,
            'sort': sort,
            'sort_mth': sort_mth
        }

        # 선택적 파라미터 추가
        if corp_code:
            params['corp_code'] = corp_code
        if bgn_de:
            params['bgn_de'] = bgn_de
        if end_de:
            params['end_de'] = end_de
        if last_reprt_at:
            params['last_reprt_at'] = last_reprt_at
        if pblntf_ty:
            params['pblntf_ty'] = pblntf_ty
        if pblntf_detail_ty:
            params['pblntf_detail_ty'] = pblntf_detail_ty
        if corp_cls:
            params['corp_cls'] = corp_cls

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ DART API 오류: {e}")
            return {'status': '013', 'message': str(e), 'list': []}

    def get_today_disclosures(
        self,
        corp_cls: Optional[str] = 'K',  # 코스닥
        pblntf_ty: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        오늘의 공시 조회

        Args:
            corp_cls: 법인구분 (K:코스닥)
            pblntf_ty: 공시유형

        Returns:
            오늘 공시 목록
        """
        today = datetime.now().strftime('%Y%m%d')

        result = self.get_disclosures(
            bgn_de=today,
            end_de=today,
            corp_cls=corp_cls,
            pblntf_ty=pblntf_ty,
            page_count=100
        )

        if result.get('status') == '000':
            return result.get('list', [])
        return []

    def search_keyword_disclosures(
        self,
        keyword: str,
        days_back: int = 7,
        corp_cls: Optional[str] = 'K'
    ) -> List[Dict[str, Any]]:
        """
        키워드로 공시 검색

        Args:
            keyword: 검색 키워드 (예: '단기과열', '상한가')
            days_back: 검색 기간 (일)
            corp_cls: 법인구분

        Returns:
            키워드가 포함된 공시 목록
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        result = self.get_disclosures(
            bgn_de=start_date.strftime('%Y%m%d'),
            end_de=end_date.strftime('%Y%m%d'),
            corp_cls=corp_cls,
            page_count=100
        )

        if result.get('status') != '000':
            return []

        # 키워드 필터링
        filtered = []
        for disclosure in result.get('list', []):
            if keyword in disclosure.get('report_nm', ''):
                filtered.append(disclosure)

        return filtered

    def get_overheat_warnings(self) -> List[Dict[str, Any]]:
        """
        단기과열종목 예고 공시 조회

        Returns:
            단기과열종목 관련 공시 목록
        """
        return self.search_keyword_disclosures('단기과열', days_back=3)

    def format_disclosure(self, disclosure: Dict[str, Any]) -> str:
        """
        공시 정보를 읽기 쉽게 포맷팅

        Args:
            disclosure: 공시 정보

        Returns:
            포맷팅된 문자열
        """
        return (
            f"📋 {disclosure.get('corp_name', '미상')} ({disclosure.get('stock_code', '')})\n"
            f"   제목: {disclosure.get('report_nm', '')}\n"
            f"   제출: {disclosure.get('rcept_dt', '')}\n"
            f"   링크: https://dart.fss.or.kr/dsaf001/main.do?rcpNo={disclosure.get('rcept_no', '')}"
        )


# 싱글톤 인스턴스
_dart_instance = None


def get_dart(api_key: Optional[str] = None) -> DartService:
    """
    DART 서비스 싱글톤 인스턴스 반환

    Args:
        api_key: DART API 키

    Returns:
        DartService 인스턴스
    """
    global _dart_instance
    if _dart_instance is None:
        _dart_instance = DartService(api_key)
    return _dart_instance


# 간편 함수들
def get_disclosures(**kwargs) -> Dict[str, Any]:
    """공시 검색"""
    return get_dart().get_disclosures(**kwargs)


def get_today_disclosures(corp_cls: Optional[str] = 'K') -> List[Dict[str, Any]]:
    """오늘의 공시"""
    return get_dart().get_today_disclosures(corp_cls)


def search_keyword(keyword: str, days_back: int = 7) -> List[Dict[str, Any]]:
    """키워드 검색"""
    return get_dart().search_keyword_disclosures(keyword, days_back)


def get_overheat_warnings() -> List[Dict[str, Any]]:
    """단기과열종목 예고"""
    return get_dart().get_overheat_warnings()