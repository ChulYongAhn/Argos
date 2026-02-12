"""
코스닥 시총 1000억 이상 상위 500개 기업 리스트 생성
- 기업명과 KIS 주식코드를 CSV로 저장
"""

import pandas as pd
from pykrx import stock
from datetime import datetime, timedelta
import time
import os

def get_latest_trading_day():
    """최근 거래일 구하기"""
    today = datetime.now()

    # 주말이면 금요일로
    if today.weekday() == 5:  # 토요일
        return (today - timedelta(days=1)).strftime('%Y%m%d')
    elif today.weekday() == 6:  # 일요일
        return (today - timedelta(days=2)).strftime('%Y%m%d')
    else:
        # 평일이면 오늘 or 어제 (장 마감 전후 체크)
        if today.hour < 16:  # 장 마감 전이면 어제
            return (today - timedelta(days=1)).strftime('%Y%m%d')
        else:
            return today.strftime('%Y%m%d')

def get_kosdaq_top_companies(min_market_cap=100_000_000_000, top_n=500):
    """
    코스닥 시총 상위 기업 가져오기

    Args:
        min_market_cap: 최소 시가총액 (기본: 1000억원)
        top_n: 상위 N개 기업 (기본: 500개)

    Returns:
        DataFrame with columns: ticker, name, market_cap
    """

    print("📊 코스닥 기업 정보 수집 시작...")

    # 최근 거래일
    target_date = get_latest_trading_day()
    print(f"📅 기준일: {target_date}")

    # 코스닥 전체 종목 코드 가져오기
    kosdaq_tickers = stock.get_market_ticker_list(target_date, market="KOSDAQ")
    print(f"📌 전체 코스닥 종목 수: {len(kosdaq_tickers)}개")

    companies = []

    print("⏳ 시가총액 계산 중... (약 2-3분 소요)")

    # 각 종목별 시가총액 계산
    for i, ticker in enumerate(kosdaq_tickers):
        try:
            # 진행상황 표시
            if (i + 1) % 50 == 0:
                print(f"   처리중: {i + 1}/{len(kosdaq_tickers)}")

            # 종목명 가져오기
            name = stock.get_market_ticker_name(ticker)

            # 시가총액 가져오기 (원 단위)
            cap_df = stock.get_market_cap(target_date, target_date, ticker)
            if cap_df.empty:
                continue

            market_cap = cap_df.iloc[0]['시가총액']

            # 1000억 이상만 저장
            if market_cap >= min_market_cap:
                companies.append({
                    'ticker': ticker,
                    'name': name,
                    'market_cap': market_cap,
                    'market_cap_억': round(market_cap / 100_000_000)  # 억 단위
                })

            # API 부하 방지
            time.sleep(0.01)

        except Exception as e:
            print(f"   ⚠️ {ticker} 처리 중 오류: {e}")
            continue

    # DataFrame 생성 및 정렬
    df = pd.DataFrame(companies)

    if df.empty:
        print("❌ 조건에 맞는 기업이 없습니다.")
        return pd.DataFrame()

    # 시가총액 기준 내림차순 정렬
    df = df.sort_values('market_cap', ascending=False).reset_index(drop=True)

    # 상위 N개만 선택 (500개 또는 전체 중 작은 값)
    df = df.head(min(top_n, len(df)))

    # 순위 추가
    df['rank'] = range(1, len(df) + 1)

    # 컬럼 순서 정리
    df = df[['rank', 'ticker', 'name', 'market_cap_억']]

    print(f"\n✅ 시총 1000억 이상 기업: {len(df)}개")

    return df

def save_to_csv(df, filename="kosdaq_top_companies.csv"):
    """DataFrame을 CSV로 저장"""

    if df.empty:
        print("❌ 저장할 데이터가 없습니다.")
        return

    # 현재 스크립트의 디렉토리 경로 가져오기
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(current_dir, filename)

    # CSV 저장
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    print(f"💾 파일 저장 완료: {filepath}")

    # 상위 10개 미리보기
    print("\n📊 상위 10개 기업:")
    print("-" * 60)
    for idx, row in df.head(10).iterrows():
        print(f"{row['rank']:3d}위 | {row['ticker']} | {row['name']:20s} | {row['market_cap_억']:,}억원")

def main():
    """메인 실행 함수"""

    print("=" * 60)
    print("🚀 코스닥 시총 상위 기업 리스트 생성기")
    print("=" * 60)

    # 데이터 수집
    df = get_kosdaq_top_companies()

    if not df.empty:
        # CSV 저장
        save_to_csv(df)

        # 통계 출력
        print("\n📈 통계:")
        print(f"  - 총 기업 수: {len(df)}개")
        print(f"  - 최대 시총: {df['market_cap_억'].max():,}억원")
        print(f"  - 최소 시총: {df['market_cap_억'].min():,}억원")
        print(f"  - 평균 시총: {df['market_cap_억'].mean():,.0f}억원")

    print("\n" + "=" * 60)
    print("✨ 작업 완료!")
    print("=" * 60)

if __name__ == "__main__":
    main()