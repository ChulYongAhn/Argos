"""
KRX 거래소 공시 간단 조회 서비스
- pykrx 활용 및 웹 데이터 수집
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pykrx import stock
import time

def GetKrxWarnings(stock_code: str) -> List[Dict[str, Any]]:
    """
    KRX 투자주의/단기과열 정보 조회 (간단 버전)

    Args:
        stock_code: 종목코드

    Returns:
        거래소 공시 리스트
    """
    warnings = []

    try:
        # 1. 투자경고/주의 종목 조회 (KRX 웹사이트 직접 조회)
        # KRX는 공개 데이터를 제공하지만 구조화된 API가 제한적

        # 네이버 증권에서 투자주의 정보 확인 (대안)
        naver_url = f"https://finance.naver.com/item/main.nhn?code={stock_code}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(naver_url, headers=headers, timeout=5)

        if response.status_code == 200:
            content = response.text

            # 투자주의/경고 텍스트 찾기
            if '투자주의' in content:
                warnings.append({
                    'date': datetime.now().strftime('%Y%m%d'),
                    'title': '투자주의종목 지정',
                    'type': 'KRX'
                })

            if '투자경고' in content:
                warnings.append({
                    'date': datetime.now().strftime('%Y%m%d'),
                    'title': '투자경고종목 지정',
                    'type': 'KRX'
                })

            if '단기과열' in content:
                warnings.append({
                    'date': datetime.now().strftime('%Y%m%d'),
                    'title': '단기과열종목 지정',
                    'type': 'KRX'
                })

        # 2. pykrx로 거래 정보 확인 (거래량 급증 등)
        today = datetime.now().strftime('%Y%m%d')
        try:
            # 최근 거래량 정보
            df = stock.get_market_ohlcv(today, today, stock_code)
            if not df.empty:
                volume = df.iloc[0]['거래량']

                # 10일 평균 거래량과 비교
                past_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
                df_past = stock.get_market_ohlcv(past_date, today, stock_code)
                if len(df_past) > 10:
                    avg_volume = df_past.tail(11).head(10)['거래량'].mean()

                    # 거래량이 평균의 5배 이상이면 거래량 급증 표시
                    if volume > avg_volume * 5:
                        warnings.append({
                            'date': today,
                            'title': f'거래량 급증 (평균 대비 {volume/avg_volume:.1f}배)',
                            'type': 'SIGNAL'
                        })
        except:
            pass

    except Exception as e:
        print(f"⚠️ KRX 정보 조회 중 오류: {e}")

    return warnings


def GetCombinedDisclosures(stock_code: str, days: int = 15) -> Dict[str, List[Dict[str, Any]]]:
    """
    DART + KRX 통합 공시 조회

    Args:
        stock_code: 종목코드
        days: 조회 기간

    Returns:
        {'dart': [...], 'krx': [...]} 형태의 통합 공시
    """
    from services.DartService.dart_service import GetDartData

    result = {
        'dart': [],
        'krx': []
    }

    try:
        # DART 공시
        result['dart'] = GetDartData(stock_code, days)
    except Exception as e:
        print(f"⚠️ DART 조회 오류: {e}")

    try:
        # KRX 공시
        result['krx'] = GetKrxWarnings(stock_code)
    except Exception as e:
        print(f"⚠️ KRX 조회 오류: {e}")

    return result


if __name__ == "__main__":
    """테스트"""
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    print("="*60)
    print("🔍 KRX + DART 통합 공시 테스트")
    print("="*60)

    test_stocks = [
        ('187660', '현대ADM'),
        ('005930', '삼성전자')
    ]

    for stock_code, name in test_stocks:
        print(f"\n📊 {name} ({stock_code})")
        print("-"*40)

        disclosures = GetCombinedDisclosures(stock_code, 15)

        # DART 공시
        if disclosures['dart']:
            print(f"\n📄 DART 공시 ({len(disclosures['dart'])}개):")
            for disc in disclosures['dart'][:3]:
                date_str = disc['date'][4:6] + '/' + disc['date'][6:8] if disc['date'] else ''
                print(f"  • {date_str} {disc['title'][:50]}")
        else:
            print("\n📄 DART 공시 없음")

        # KRX 공시
        if disclosures['krx']:
            print(f"\n⚠️ KRX 공시 ({len(disclosures['krx'])}개):")
            for disc in disclosures['krx']:
                date_str = disc['date'][4:6] + '/' + disc['date'][6:8] if disc['date'] else ''
                print(f"  • {date_str} {disc['title']}")
        else:
            print("\n⚠️ KRX 공시 없음")

        time.sleep(1)  # API 부하 방지