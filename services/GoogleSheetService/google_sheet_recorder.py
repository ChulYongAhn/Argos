"""
구글 시트 거래 기록 모듈 - Argos 암호화폐 자동매매
실시간으로 코인 매매 내역을 구글 시트에 기록
"""

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


class GoogleSheetRecorder:
    """구글 시트 거래 기록 클래스"""

    def __init__(self, credentials_file: str = None, sheet_id: str = None):
        """
        초기화

        Args:
            credentials_file: 서비스 계정 인증 JSON 파일 경로
            sheet_id: 구글 시트 ID
        """
        # 환경 변수에서 설정 로드
        self.credentials_file = credentials_file or os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
        self.sheet_id = sheet_id or os.getenv('ARGOS_SHEET_ID')

        if not self.sheet_id:
            raise ValueError("구글 시트 ID가 필요합니다. ARGOS_SHEET_ID 환경변수를 설정하세요.")

        # 구글 시트 연결
        self.client = self._authenticate()
        self.spreadsheet = None
        self.trades_sheet = None
        self.summary_sheet = None

        # 시트 초기화
        self._initialize_sheets()

        # 거래 데이터 임시 저장 (매수-매도 매칭용)
        self.current_positions = {}  # 현재 보유 포지션

    def _authenticate(self):
        """구글 시트 API 인증"""
        try:
            # 인증 범위 설정
            scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]

            # 서비스 계정 인증
            creds = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=scope
            )

            # gspread 클라이언트 생성
            return gspread.authorize(creds)

        except FileNotFoundError:
            print(f"❌ 인증 파일을 찾을 수 없습니다: {self.credentials_file}")
            print("   구글 클라우드 콘솔에서 서비스 계정을 생성하고 JSON 키를 다운로드하세요.")
            raise
        except Exception as e:
            print(f"❌ 인증 실패: {e}")
            raise

    def _initialize_sheets(self):
        """시트 초기화 및 헤더 설정"""
        try:
            # 스프레드시트 열기
            self.spreadsheet = self.client.open_by_key(self.sheet_id)

            # 거래내역 시트 설정
            self._setup_trades_sheet()

            # 일별 요약 시트 설정
            self._setup_summary_sheet()

            print(f"✅ 구글 시트 연결 성공: {self.spreadsheet.title}")

        except Exception as e:
            print(f"❌ 시트 초기화 실패: {e}")
            raise

    def _setup_trades_sheet(self):
        """거래내역 시트 설정"""
        sheet_name = "거래내역"

        # 시트 생성 또는 가져오기
        try:
            self.trades_sheet = self.spreadsheet.worksheet(sheet_name)
        except:
            self.trades_sheet = self.spreadsheet.add_worksheet(
                title=sheet_name, rows=10000, cols=12
            )

        # 헤더가 없으면 추가
        if not self.trades_sheet.get_all_values():
            headers = [
                "거래시간", "거래타입", "코인", "심볼", "매수가격", "매도가격",
                "수량", "매수금액", "매도금액", "수익률(%)", "수익금", "메모"
            ]
            self.trades_sheet.append_row(headers)

            # 헤더 스타일 설정 (굵게)
            self.trades_sheet.format('A1:L1', {'textFormat': {'bold': True}})

    def _setup_summary_sheet(self):
        """일별 요약 시트 설정"""
        sheet_name = "일별요약"

        # 시트 생성 또는 가져오기
        try:
            self.summary_sheet = self.spreadsheet.worksheet(sheet_name)
        except:
            self.summary_sheet = self.spreadsheet.add_worksheet(
                title=sheet_name, rows=1000, cols=8
            )

        # 헤더가 없으면 추가
        if not self.summary_sheet.get_all_values():
            headers = [
                "날짜", "거래횟수", "승률(%)", "총수익금", "평균수익률(%)",
                "최고수익", "최대손실", "누적수익금"
            ]
            self.summary_sheet.append_row(headers)
            self.summary_sheet.format('A1:H1', {'textFormat': {'bold': True}})

    def record_buy(self, symbol: str, coin_name: str, price: float,
                   quantity: float, amount: float = None, memo: str = ""):
        """
        매수 기록 (포지션 정보만 저장, 시트에는 매도 시 기록)

        Args:
            symbol: 마켓 심볼 (예: KRW-BTC)
            coin_name: 코인 이름 (예: 비트코인)
            price: 매수가
            quantity: 수량
            amount: 매수금액 (없으면 자동계산)
            memo: 메모
        """
        try:
            now = datetime.now()
            amount = amount or (price * quantity)

            # 포지션 정보 저장 (매도 시 한 번에 기록용)
            self.current_positions[symbol] = {
                "coin_name": coin_name,
                "buy_price": price,
                "quantity": quantity,
                "buy_time": now,
                "buy_amount": amount,
                "memo": memo
            }

            print(f"📝 포지션 저장: {coin_name}({symbol}) 매수 - {amount:,.0f}원")

        except Exception as e:
            print(f"❌ 매수 정보 저장 실패: {e}")

    def record_sell(self, symbol: str, coin_name: str, price: float,
                   quantity: float, sell_type: str = "수동", memo: str = ""):
        """
        매도 기록 (매수-매도 정보를 한 행에 기록)

        Args:
            symbol: 마켓 심볼 (예: KRW-BTC)
            coin_name: 코인 이름 (예: 비트코인)
            price: 매도가
            quantity: 수량
            sell_type: 매도유형 (익절/손절/청산/수동)
            memo: 메모
        """
        try:
            now = datetime.now()
            sell_amount = price * quantity

            # 매수 정보 가져오기
            buy_price = 0
            buy_amount = 0
            profit_rate = 0
            profit_amount = 0

            if symbol in self.current_positions:
                position = self.current_positions[symbol]
                buy_price = position["buy_price"]
                buy_amount = position["buy_amount"]

                # 원래 메모와 새 메모 합치기
                full_memo = f"{position.get('memo', '')} | {memo}".strip(' |')

                # 수익률 및 수익금 계산
                if buy_amount > 0:
                    profit_rate = ((sell_amount - buy_amount) / buy_amount) * 100
                    profit_amount = sell_amount - buy_amount
            else:
                # 포지션 정보가 없는 경우 (프로그램 재시작 등)
                full_memo = memo

            # 거래내역 시트에 기록
            row = [
                now.strftime("%Y-%m-%d %H:%M:%S"),  # 거래시간
                sell_type,                           # 거래타입
                coin_name,                            # 코인
                symbol,                               # 심볼
                buy_price,                            # 매수가격
                price,                                # 매도가격
                quantity,                             # 수량
                buy_amount,                           # 매수금액
                sell_amount,                          # 매도금액
                round(profit_rate, 2),                # 수익률
                round(profit_amount, 0),              # 수익금
                full_memo                             # 메모
            ]

            self.trades_sheet.append_row(row)

            # 수익률에 따른 색상 설정
            last_row = len(self.trades_sheet.get_all_values())

            # 수익률 색상 (양수: 빨간색, 음수: 파란색)
            if profit_rate > 0:
                profit_color = {'red': 0.8, 'green': 0.0, 'blue': 0.0}  # 빨간색 (수익)
                emoji = "🟢"
            else:
                profit_color = {'red': 0.0, 'green': 0.0, 'blue': 0.8}  # 파란색 (손실)
                emoji = "🔴"

            self.trades_sheet.format(f'J{last_row}:K{last_row}', {
                'textFormat': {'foregroundColor': profit_color}
            })

            # 포지션 제거
            if symbol in self.current_positions:
                del self.current_positions[symbol]

            print(f"📝 구글시트 기록: {coin_name} {sell_type} (수익률: {profit_rate:+.2f}%)")

        except Exception as e:
            print(f"❌ 매도 기록 실패: {e}")

    def update_daily_summary(self):
        """일별 요약 업데이트"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")

            # 오늘 거래 내역 가져오기
            all_trades = self.trades_sheet.get_all_values()[1:]  # 헤더 제외
            today_trades = [t for t in all_trades if t[0].startswith(today)]

            if not today_trades:
                return

            # 통계 계산
            total_trades = len(today_trades)
            wins = [t for t in today_trades if float(t[9]) > 0]  # 수익률이 양수
            win_rate = (len(wins) / total_trades * 100) if total_trades > 0 else 0

            profits = [float(t[10]) for t in today_trades if t[10]]  # 수익금
            total_profit = sum(profits)

            profit_rates = [float(t[9]) for t in today_trades if t[9]]  # 수익률
            avg_profit_rate = sum(profit_rates) / len(profit_rates) if profit_rates else 0

            max_profit = max(profits) if profits else 0
            max_loss = min(profits) if profits else 0

            # 누적 수익금 계산 (이전 날짜들 포함)
            all_profits = [float(t[10]) for t in all_trades if t[10]]
            cumulative_profit = sum(all_profits)

            # 일별 요약 시트에 업데이트
            summary_data = self.summary_sheet.get_all_values()[1:]  # 헤더 제외
            today_row_index = None

            # 오늘 날짜 행 찾기
            for i, row in enumerate(summary_data):
                if row[0] == today:
                    today_row_index = i + 2  # 헤더 고려
                    break

            row_data = [
                today,
                total_trades,
                round(win_rate, 1),
                round(total_profit, 0),
                round(avg_profit_rate, 2),
                round(max_profit, 0),
                round(max_loss, 0),
                round(cumulative_profit, 0)
            ]

            if today_row_index:
                # 업데이트
                cell_list = self.summary_sheet.range(f'A{today_row_index}:H{today_row_index}')
                for i, cell in enumerate(cell_list):
                    cell.value = row_data[i]
                self.summary_sheet.update_cells(cell_list)
            else:
                # 새로 추가
                self.summary_sheet.append_row(row_data)

            print(f"📊 일별 요약 업데이트: 거래 {total_trades}건, 승률 {win_rate:.1f}%, 수익 {total_profit:+,.0f}원")

        except Exception as e:
            print(f"❌ 일별 요약 업데이트 실패: {e}")

    def get_sheet_url(self) -> str:
        """구글 시트 URL 반환"""
        return f"https://docs.google.com/spreadsheets/d/{self.sheet_id}"

    def add_test_record(self, coin_name: str, symbol: str,
                       buy_price: float, sell_price: float, quantity: float):
        """테스트용 기록 추가 (매수/매도 한 번에)"""
        try:
            # 매수 기록
            self.record_buy(symbol, coin_name, buy_price, quantity)

            # 매도 기록
            self.record_sell(symbol, coin_name, sell_price, quantity, "테스트")

            # 일별 요약 업데이트
            self.update_daily_summary()

        except Exception as e:
            print(f"❌ 테스트 기록 실패: {e}")


# 싱글톤 인스턴스
_recorder_instance = None


def get_recorder() -> GoogleSheetRecorder:
    """구글 시트 레코더 싱글톤 인스턴스 반환"""
    global _recorder_instance
    if _recorder_instance is None:
        _recorder_instance = GoogleSheetRecorder()
    return _recorder_instance


# 테스트 코드
if __name__ == "__main__":
    print("구글 시트 연동 테스트 - Argos")
    print("=" * 50)

    # 레코더 생성
    recorder = GoogleSheetRecorder()

    # 테스트 1: 익절 시뮬레이션
    print("\n[테스트 1: 익절]")
    recorder.add_test_record(
        coin_name="비트코인",
        symbol="KRW-BTC",
        buy_price=140000000,
        sell_price=144200000,
        quantity=0.001
    )

    # 테스트 2: 손절 시뮬레이션
    print("\n[테스트 2: 손절]")
    recorder.add_test_record(
        coin_name="이더리움",
        symbol="KRW-ETH",
        buy_price=5000000,
        sell_price=4750000,
        quantity=0.1
    )

    # 테스트 3: 소액 익절
    print("\n[테스트 3: 리플 거래]")
    recorder.add_test_record(
        coin_name="리플",
        symbol="KRW-XRP",
        buy_price=3500,
        sell_price=3605,
        quantity=100
    )

    # URL 출력
    print(f"\n📱 구글 시트 URL: {recorder.get_sheet_url()}")
    print("✅ 구글 시트에서 확인하세요!")