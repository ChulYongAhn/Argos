"""
상따봇 (SangddaBot) - 코스닥 상한가 추적 봇
매일 저녁 8시 1분에 코스닥 상한가 종목을 찾아 Slack으로 알림
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from pykrx import stock
import time
from dotenv import load_dotenv

# Argos 루트 경로를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 공통 서비스 import
from services.SlackService import slack
from services.SimpleGoogleSheetService import SimpleGoogleSheet
from services.DartService import get_dart

# .env 파일 로드
load_dotenv()


class SangddaBot:
    """코스닥 상한가 추적 봇"""

    def __init__(self):
        """초기화"""
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.csv_path = os.path.join(self.current_dir, 'kosdaq_top_companies.csv')
        self.slack_webhook = os.getenv('SLACK_WEBHOOK')
        self.sheet_id = os.getenv('GOOGLE_SHEET_ID_3')  # 상한가 시트 ID
        self.sheet_name = os.getenv('GOOGLE_SHEET_NAME_3', '상한가')  # 상한가 시트명 (기본값: 상한가)

        # 구글 시트 서비스 초기화
        if self.sheet_id:
            # GoogleSheetService 폴더의 credentials.json 사용
            cred_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                'services', 'GoogleSheetService', 'credentials.json'
            )
            # 환경변수에서 지정한 시트명 사용
            self.sheet_service = SimpleGoogleSheet(
                sheet_id=self.sheet_id,
                credentials_file=cred_path,
                sheet_name=self.sheet_name
            )
            if self.sheet_service.enabled:
                print(f"✅ 구글 시트 연결 성공: {self.sheet_service.spreadsheet.title}")
            else:
                print("❌ 구글 시트 연결 실패")
        else:
            self.sheet_service = None

    def get_latest_trading_day(self):
        """최근 거래일 구하기 (저녁 8시 실행 기준)"""
        today = datetime.now()

        # 주말 처리
        if today.weekday() == 5:  # 토요일
            return (today - timedelta(days=1)).strftime('%Y%m%d')
        elif today.weekday() == 6:  # 일요일
            return (today - timedelta(days=2)).strftime('%Y%m%d')
        else:
            # 평일 - 저녁 8시에 실행하므로 무조건 오늘 날짜 사용
            # (pykrx는 장 마감 후 약 30분~1시간 후부터 데이터 제공)
            return today.strftime('%Y%m%d')

    def get_limit_up_price(self, prev_close):
        """정확한 상한가 가격 계산"""
        theoretical = prev_close * 1.3

        # 호가 단위 적용
        if theoretical < 1000:
            tick = 1
        elif theoretical < 5000:
            tick = 5
        elif theoretical < 10000:
            tick = 10
        elif theoretical < 50000:
            tick = 50
        elif theoretical < 100000:
            tick = 100
        elif theoretical < 500000:
            tick = 500
        else:
            tick = 1000

        # 호가 단위로 내림
        return int(theoretical // tick) * tick

    def is_limit_up(self, prev_close, current_price):
        """상한가 여부 판별"""
        limit_price = self.get_limit_up_price(prev_close)
        return current_price == limit_price

    def get_price_history(self, ticker, end_date, days=10):
        """10거래일 가격 변동률 가져오기 (오늘 제외, 어제부터)"""
        try:
            # 어제부터 시작 (오늘 제외)
            yesterday = (datetime.strptime(end_date, '%Y%m%d') - timedelta(days=1)).strftime('%Y%m%d')
            # 충분한 기간 설정 (주말 포함 고려, 20일 정도)
            start_date = (datetime.strptime(yesterday, '%Y%m%d') - timedelta(days=20)).strftime('%Y%m%d')

            # 어제까지의 데이터만 가져오기
            df = stock.get_market_ohlcv(start_date, yesterday, ticker)

            if len(df) < 2:
                return []

            # 최근 11거래일 데이터 사용 (10일 등락률 계산용)
            df = df.tail(11)

            # 등락률 계산 (역순으로 D-1부터 D-10까지)
            history = []
            for i in range(len(df)-1, 0, -1):  # 역순 (최근부터)
                prev_close = df.iloc[i-1]['종가']
                curr_close = df.iloc[i]['종가']
                change_rate = ((curr_close - prev_close) / prev_close) * 100
                history.append(round(change_rate, 2))

            # 10거래일만 반환 (D-1 ~ D-10)
            return history[:10]

        except Exception as e:
            print(f"   ⚠️ {ticker} 가격 이력 조회 실패: {e}")
            return []

    def load_kosdaq_companies(self):
        """CSV에서 코스닥 기업 목록 로드"""
        try:
            if not os.path.exists(self.csv_path):
                print("❌ kosdaq_top_companies.csv 파일이 없습니다.")
                print("   먼저 KosdaqList.py를 실행하세요.")
                return None

            df = pd.read_csv(self.csv_path)
            print(f"✅ {len(df)}개 기업 목록 로드 완료")
            return df
        except Exception as e:
            print(f"❌ CSV 로드 실패: {e}")
            return None

    def get_recent_disclosures(self, corp_name, ticker=None, days=15):
        """특정 기업의 최근 공시 조회 (모든 공시)"""
        try:
            # DART 서비스 초기화
            dart = get_dart()

            # 기간 설정
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # 코스닥 전체 공시 조회 (여러 페이지)
            all_disclosures = []
            for page in range(1, 3):  # 2페이지까지 (200개)
                result = dart.get_disclosures(
                    bgn_de=start_date.strftime('%Y%m%d'),
                    end_de=end_date.strftime('%Y%m%d'),
                    corp_cls='K',  # 코스닥
                    page_no=page,
                    page_count=100
                )
                if result.get('status') == '000':
                    all_disclosures.extend(result.get('list', []))
                else:
                    break

            if not all_disclosures:
                return []

            # 회사명 또는 종목코드로 필터링
            disclosures = []
            for disc in all_disclosures:
                disc_corp_name = disc.get('corp_name', '')
                disc_stock_code = disc.get('stock_code', '')

                # 회사명 매칭 (부분 일치) 또는 종목코드 매칭
                matched = False
                if ticker and disc_stock_code == ticker:
                    matched = True
                elif corp_name in disc_corp_name:
                    matched = True

                if matched:
                    disclosures.append({
                        'date': disc.get('rcept_dt', ''),
                        'title': disc.get('report_nm', ''),
                        'link': f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={disc.get('rcept_no', '')}"
                    })

            # 최근 3개만 반환
            return disclosures[:3]

        except Exception as e:
            print(f"   ⚠️ DART 공시 조회 실패: {e}")
            return []

    def find_limit_up_stocks(self):
        """상한가 종목 찾기"""
        # 기업 목록 로드
        companies_df = self.load_kosdaq_companies()
        if companies_df is None:
            return []

        # 최근 거래일
        target_date = self.get_latest_trading_day()
        print(f"📅 기준일: {target_date}")

        limit_up_stocks = []
        total = len(companies_df)

        print(f"🔍 상한가 종목 검색 중... (총 {total}개)")

        for idx, row in companies_df.iterrows():
            ticker = row['ticker']
            name = row['name']

            # 진행상황 표시
            if (idx + 1) % 50 == 0:
                print(f"   처리중: {idx + 1}/{total}")

            try:
                # get_market_ohlcv 사용 (더 안정적)
                df = stock.get_market_ohlcv(target_date, target_date, ticker)
                if df.empty:
                    print(f"{ticker} {name[:10]:10s} | 데이터 없음")
                    continue

                # 현재가와 등락률
                current_price = df.iloc[0]['종가']
                change_rate = df.iloc[0]['등락률']

                # 전일 종가 계산 (현재가에서 등락분 빼기)
                prev_close = current_price / (1 + change_rate/100)

                # 간단히 출력 (종목당 한 줄)
                print(f"{ticker} {name[:10]:10s} | 종가: {current_price:7.0f} | 등락률: {change_rate:+6.2f}%")

                # 전일 종가가 0이면 스킵
                if prev_close == 0:
                    continue

                # 상한가 체크
                if self.is_limit_up(prev_close, current_price):
                    # 10거래일 이력
                    history = self.get_price_history(ticker, target_date)

                    # DART 공시 조회 (모든 공시) - 종목코드도 함께 전달
                    disclosures = self.get_recent_disclosures(name, ticker=ticker)

                    limit_up_stocks.append({
                        'ticker': ticker,
                        'name': name,
                        'price': current_price,
                        'change_rate': round(change_rate, 2),
                        'history': history,
                        'disclosures': disclosures
                    })

                    print(f"   🔥 상한가 발견!")

                # API 부하 방지
                time.sleep(0.01)

            except Exception as e:
                # 에러는 조용히 처리
                continue

        print(f"\n✅ 상한가 종목: {len(limit_up_stocks)}개 발견")
        return limit_up_stocks

    def format_slack_message(self, stocks):
        """Slack 메시지 포맷"""
        if not stocks:
            return "📊 오늘은 코스닥 상한가 종목이 없습니다."

        today = datetime.now().strftime('%Y.%m.%d')
        weekday = ['월', '화', '수', '목', '금', '토', '일'][datetime.now().weekday()]

        message = f"📈 코스닥 상한가 [{today} {weekday}]\n\n"

        for stock in stocks:
            # 상한가 종목은 불 이모티콘과 볼드 처리
            message += f"🔥 *{stock['name']}({stock['ticker']}) | {stock['price']:,} | +{stock['change_rate']}%*\n"

            # 10거래일 이력
            if stock['history']:
                history_str = " | ".join([f"D-{i+1}: {'+' if h > 0 else ''}{h}%"
                                         for i, h in enumerate(stock['history'])])
                message += f"└ {history_str}\n"

            # DART 공시 정보 (모든 공시)
            if stock.get('disclosures'):
                for disc in stock['disclosures']:
                    date_str = disc['date'][4:6] + '/' + disc['date'][6:8] if disc['date'] else ''
                    # 공시 종류에 따라 아이콘 구분
                    icon = "📢"
                    if any(keyword in disc['title'] for keyword in ["단기과열", "투자위험", "거래정지", "관리종목"]):
                        icon = "⚠️"
                    elif any(keyword in disc['title'] for keyword in ["실적", "매출", "계약", "수주", "공급"]):
                        icon = "💰"

                    # 슬랙 웹훅은 링크를 지원하지 않으므로 텍스트와 URL을 함께 표시
                    message += f"└ {icon} {date_str} {disc['title']}\n"
                    if disc.get('link'):
                        message += f"   {disc['link']}\n"

            message += "\n"

        message += f"총 {len(stocks)}개 종목\n"
        message += "※ D-1 = 직전 거래일, D-10 = 10거래일전\n\n"

        # 구글 시트 링크 추가 (슬랙 웹훅은 링크를 지원하지 않으므로 URL 직접 표시)
        if self.sheet_id:
            sheet_url = f"https://docs.google.com/spreadsheets/d/{self.sheet_id}"
            message += f"📊 구글 시트: {sheet_url}"

        return message

    def write_to_sheet(self, stocks):
        """구글 시트에 상한가 종목 기록"""
        if not self.sheet_service or not self.sheet_service.enabled:
            print("⚠️ 구글 시트가 연결되지 않았습니다.")
            return

        try:
            # "상한가" 시트 사용
            worksheet = self.sheet_service.worksheet

            # 헤더 확인 및 추가
            all_values = worksheet.get_all_values()
            if not all_values:
                headers = ['날짜', '종목명', '종목코드', '종가', '등락률', 'D-1', 'D-2', 'D-3', 'D-4', 'D-5', 'D-6', 'D-7', 'D-8', 'D-9', 'D-10', '공시']
                worksheet.append_row(headers)
                # 헤더 굵게
                worksheet.format('1:1', {'textFormat': {'bold': True}})
                print(f"✅ '상한가' 시트에 헤더 추가")

            # 데이터 준비 및 추가
            today = datetime.now().strftime('%Y-%m-%d')

            for stock in stocks:
                # 공시 정보 정리
                disclosure_text = ""
                if stock.get('disclosures'):
                    disc_list = []
                    for disc in stock['disclosures'][:2]:  # 최대 2개
                        disc_list.append(f"{disc['title'][:30]}")
                    disclosure_text = " / ".join(disc_list)

                # 데이터 준비 (가변 인자로 전달할 데이터들)
                data_args = [
                    today,
                    stock['name'],
                    stock.get('ticker', ''),
                    stock.get('price', ''),
                    f"+{stock['change_rate']}%"
                ]

                # 10일 이력 추가
                history = stock.get('history', [])
                for i in range(10):
                    if i < len(history):
                        data_args.append(f"{'+' if history[i] > 0 else ''}{history[i]}%")
                    else:
                        data_args.append('')  # 데이터가 없으면 빈칸

                # 공시 정보 추가
                data_args.append(disclosure_text)

                # append_data 메서드로 가변 인자 전달
                self.sheet_service.append_data(*data_args)

            if stocks:
                print(f"✅ 구글 시트 '상한가'에 {len(stocks)}개 종목 기록 완료")
            else:
                print("⚠️ 기록할 상한가 종목이 없습니다.")

        except Exception as e:
            print(f"❌ 구글 시트 기록 실패: {e}")
            import traceback
            traceback.print_exc()

    def run(self):
        """메인 실행"""
        print("=" * 60)
        print("🚀 상따봇 (SangddaBot) 시작")
        print("=" * 60)

        # 1. 상한가 종목 찾기
        stocks = self.find_limit_up_stocks()

        # 2. 구글 시트 기록
        if stocks:
            self.write_to_sheet(stocks)

        # 3. Slack 알림
        if stocks or True:  # 상한가가 없어도 알림
            message = self.format_slack_message(stocks)

            try:
                if slack(message, self.slack_webhook):
                    print("✅ Slack 메시지 전송 완료")
                else:
                    print("❌ Slack 메시지 전송 실패")
            except Exception as e:
                print(f"❌ Slack 전송 오류: {e}")

        print("\n" + "=" * 60)
        print("✨ 상따봇 실행 완료!")
        print("=" * 60)


def main():
    """메인 함수"""
    bot = SangddaBot()
    bot.run()


if __name__ == "__main__":
    main()