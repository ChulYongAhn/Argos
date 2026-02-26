"""
MinCoinBot - 업비트 멀티 종목 듀얼 타임프레임 가상 매매 시뮬레이션 봇
매도 체크: 1분봉 / 매수 체크: 5분봉
config.json의 symbols 배열에 나열된 종목을 전부 돌림
"""

import requests
import json
import logging
import time
import os
import sys
from datetime import datetime

# 상위 디렉토리 경로 추가 (services import용)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.SimpleGoogleSheetService import Send
from services.SlackService.simple_slack import SimpleSlack

# 현재 파일 기준 디렉토리
BOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BOT_DIR, "config.json")
STATE_PATH = os.path.join(BOT_DIR, "state.json")


class MinCoinBot:

    def __init__(self):
        self.config = self.load_config()
        self.state = self.load_state()
        self.slack = SimpleSlack()
        self.logger = self.setup_logging()
        self.symbols = self.config["symbols"]

        # state에 새 종목이 추가된 경우 자동 초기화
        for symbol in self.symbols:
            if symbol not in self.state["symbols"]:
                self.state["symbols"][symbol] = {
                    "holding_qty": 0.0,
                    "holding_avg_price": 0.0,
                    "total_buy_amount": 0.0,
                    "is_first_candle": True,
                }
                self.logger.info(f"새 종목 추가: {symbol}")

        self.logger.info("MinCoinBot 초기화 완료")
        self.logger.info(f"종목: {', '.join(self.symbols)}")
        self.logger.info(f"설정: 매도체크={self.config['sell_check_interval']}분봉, "
                         f"매수체크={self.config['buy_check_interval']}분봉, "
                         f"매수금={self.config['buy_amount']:,}원, "
                         f"익절={self.config['take_profit_rate']}%")
        self.logger.info(f"잔고: {self.state['balance']:,.0f}원")

    def setup_logging(self) -> logging.Logger:
        logger = logging.getLogger("MinCoinBot")
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 파일 핸들러
        log_path = os.path.join(BOT_DIR, f"mincoinbot_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def load_config(self) -> dict:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)

    def load_state(self) -> dict:
        with open(STATE_PATH, "r") as f:
            return json.load(f)

    def save_state(self):
        with open(STATE_PATH, "w") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def get_candle_data(self, symbol: str, interval: int) -> dict:
        """업비트 API로 종목의 직전 봉 데이터 조회"""
        market = f"KRW-{symbol}"
        url = f"https://api.upbit.com/v1/candles/minutes/{interval}"
        params = {"market": market, "count": 2}
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        # data[0] = 현재(진행중) 봉, data[1] = 직전(완성된) 봉
        current_price = float(data[0]["trade_price"])
        prev_open = float(data[1]["opening_price"])
        prev_close = float(data[1]["trade_price"])

        return {
            "current_price": current_price,
            "prev_open": prev_open,
            "prev_close": prev_close,
            "is_prev_bearish": prev_close < prev_open,
            "is_prev_bullish": prev_close > prev_open,
        }

    def calculate_profit_rate(self, symbol: str, current_price: float) -> float:
        """평단 대비 수익률(%) 계산"""
        avg_price = self.state["symbols"][symbol]["holding_avg_price"]
        if avg_price <= 0:
            return 0.0
        return (current_price - avg_price) / avg_price * 100

    def virtual_buy(self, symbol: str, current_price: float):
        """가상 매수 (buy_amount원어치)"""
        buy_amount = self.config["buy_amount"]
        sym_state = self.state["symbols"][symbol]

        # 잔고 부족 체크
        if self.state["balance"] < buy_amount:
            self.logger.warning(f"[{symbol}] 잔고 부족! 잔고={self.state['balance']:,.0f}원, 필요={buy_amount:,}원")
            return

        # 수수료 차감 후 실투자금
        fee = buy_amount * (self.config["buy_fee_rate"] / 100)
        actual_invest = buy_amount - fee
        buy_qty = actual_invest / current_price

        # 평단 재계산 (가중평균)
        prev_qty = sym_state["holding_qty"]
        prev_total = sym_state["total_buy_amount"]
        new_qty = prev_qty + buy_qty
        new_total = prev_total + buy_amount

        if new_qty > 0:
            sym_state["holding_avg_price"] = (prev_qty * sym_state["holding_avg_price"] + actual_invest) / new_qty
        sym_state["holding_qty"] = new_qty
        sym_state["total_buy_amount"] = new_total
        self.state["balance"] -= buy_amount

        self.logger.info(
            f"[{symbol} 매수] 가격={current_price:,.0f}원 | "
            f"수량={buy_qty:.8f} | 수수료={fee:.1f}원 | "
            f"평단={sym_state['holding_avg_price']:,.0f}원 | "
            f"총보유={new_qty:.8f} | 잔고={self.state['balance']:,.0f}원"
        )

        # 구글시트 기록
        now = datetime.now()
        eval_amount = self.state["balance"] + self.get_total_eval(current_price, symbol)
        profit_rate = self.calculate_profit_rate(symbol, current_price)
        symbol_eval = new_qty * current_price
        self.write_sheet(
            now, symbol, current_price,
            buy_amount, 0,
            eval_amount, self.state["balance"], new_total, profit_rate,
            symbol_eval, 0
        )

    def virtual_sell(self, symbol: str, current_price: float, reason: str):
        """가상 전량 매도"""
        sym_state = self.state["symbols"][symbol]
        holding_qty = sym_state["holding_qty"]
        total_buy_amount = sym_state["total_buy_amount"]

        # 매도 금액 및 수수료
        gross_sell = holding_qty * current_price
        fee = gross_sell * (self.config["sell_fee_rate"] / 100)
        net_sell = gross_sell - fee

        # 손익 계산
        profit = net_sell - total_buy_amount
        profit_rate = self.calculate_profit_rate(symbol, current_price)

        # 잔고 반영
        self.state["balance"] += net_sell
        self.state["total_realized_profit"] = self.state.get("total_realized_profit", 0) + profit

        self.logger.info(
            f"[{symbol} {reason}] 가격={current_price:,.0f}원 | "
            f"매도금={net_sell:,.0f}원 | 수수료={fee:.1f}원 | "
            f"손익={profit:+,.0f}원 ({profit_rate:+.2f}%) | "
            f"누적실현익={self.state['total_realized_profit']:+,.0f}원 | "
            f"잔고={self.state['balance']:,.0f}원"
        )

        # state 리셋 → 다시 첫 봉부터 (시트/슬랙 계산 전에 리셋해야 이중계산 방지)
        sym_state["holding_qty"] = 0.0
        sym_state["holding_avg_price"] = 0.0
        sym_state["total_buy_amount"] = 0.0
        sym_state["is_first_candle"] = True

        # 구글시트 기록
        now = datetime.now()
        symbol_eval = 0  # 전량 매도 후 해당 종목 평가금 = 0
        eval_amount = self.state["balance"] + self.get_total_eval(current_price, symbol)
        self.write_sheet(
            now, symbol, current_price,
            0, net_sell,
            eval_amount, self.state["balance"], 0, profit_rate,
            symbol_eval, profit
        )

        # 슬랙 알림
        self.slack.send(
            f"[Argos-MinCoinBot] {symbol} {reason} | "
            f"수익률: {profit_rate:+.2f}% | "
            f"수익금: {profit:+,.0f}원 | "
            f"총평가액: {eval_amount:,.0f}원"
        )

    def get_total_eval(self, current_price: float, current_symbol: str) -> float:
        """전체 보유 종목의 평가금액 합산 (현재 처리중인 종목은 current_price 사용)"""
        total = 0.0
        for symbol, sym_state in self.state["symbols"].items():
            if sym_state["holding_qty"] > 0:
                if symbol == current_symbol:
                    total += sym_state["holding_qty"] * current_price
                else:
                    total += sym_state["holding_qty"] * sym_state["holding_avg_price"]
        return total

    def write_sheet(self, now: datetime, symbol: str, current_price: float,
                     buy_amount: float, sell_amount: float,
                     eval_amount: float, cash: float, invest_amount: float,
                     profit_rate: float, symbol_eval: float, profit: float):
        """구글시트 기록 (날짜/시간/종목이름/현재가/매수액/매도액/총평가액/현금/투자금액/수익률/종목평가금/순이익)"""
        sheet_name = os.getenv("GOOGLE_SHEET_NAME_4", "민코인봇")
        try:
            Send(
                sheet_name,
                now.strftime("%Y-%m-%d"),
                now.strftime("%H:%M:%S"),
                symbol,
                str(int(current_price)),
                str(int(buy_amount)),
                str(int(sell_amount)),
                str(int(eval_amount)),
                str(int(cash)),
                str(int(invest_amount)),
                f"{profit_rate:+.2f}%",
                str(int(symbol_eval)),
                str(int(profit)),
            )
        except Exception as e:
            self.logger.error(f"구글시트 기록 실패: {e}")

    def process_symbol(self, symbol: str, loop_count: int):
        """개별 종목 처리"""
        sell_interval = self.config["sell_check_interval"]
        buy_interval = self.config["buy_check_interval"]
        sym_state = self.state["symbols"][symbol]

        # 1분봉 데이터 조회 (매도 체크용)
        candle_1m = self.get_candle_data(symbol, sell_interval)
        current_price = candle_1m["current_price"]

        if sym_state["is_first_candle"]:
            # 첫 봉: 무조건 매수
            self.logger.info(f"--- [{symbol}] 첫 봉 진입 (현재가: {current_price:,.0f}원) ---")
            self.virtual_buy(symbol, current_price)
            sym_state["is_first_candle"] = False
        else:
            profit_rate = self.calculate_profit_rate(symbol, current_price)
            avg_price = sym_state["holding_avg_price"]

            # 매도 체크 (매 1분): 수익률 ≥ +1.5% 이면 즉시 매도
            if profit_rate >= self.config["take_profit_rate"]:
                self.virtual_sell(symbol, current_price, "익절")

            # 매수 체크 (매 5분)
            elif loop_count % buy_interval == 0:
                candle_5m = self.get_candle_data(symbol, buy_interval)
                candle_type = "음봉" if candle_5m["is_prev_bearish"] else "양봉"

                self.logger.info(
                    f"[{symbol} 매수체크] 현재가={current_price:,.0f}원 | "
                    f"평단={avg_price:,.0f}원 | "
                    f"수익률={profit_rate:+.2f}% | "
                    f"직전5분봉={candle_type}"
                )

                if candle_5m["is_prev_bearish"] and current_price < avg_price:
                    self.virtual_buy(symbol, current_price)
                else:
                    self.logger.info(f"[{symbol} 대기] 매수 조건 미충족")

            else:
                self.logger.debug(
                    f"[{symbol}] 현재가={current_price:,.0f}원 | "
                    f"수익률={profit_rate:+.2f}% | "
                    f"매수체크까지 {buy_interval - (loop_count % buy_interval)}분"
                )

    def run(self):
        """메인 실행 루프 (1분마다 매도 체크, 5분마다 매수 체크) - 전 종목 순회"""
        sell_interval = self.config["sell_check_interval"]
        buy_interval = self.config["buy_check_interval"]
        loop_count = 0

        self.logger.info(f"MinCoinBot 시작 (종목: {', '.join(self.symbols)} | "
                         f"매도체크: {sell_interval}분봉, 매수체크: {buy_interval}분봉)")

        while True:
            try:
                loop_count += 1

                for symbol in self.symbols:
                    self.process_symbol(symbol, loop_count)

                self.save_state()
                time.sleep(sell_interval * 60)  # 1분마다 루프

            except KeyboardInterrupt:
                self.logger.info("사용자 중단 (Ctrl+C)")
                self.save_state()
                break
            except requests.exceptions.RequestException as e:
                self.logger.error(f"API 호출 실패: {e}")
                time.sleep(10)
            except Exception as e:
                self.logger.error(f"오류 발생: {e}", exc_info=True)
                time.sleep(10)


if __name__ == "__main__":
    bot = MinCoinBot()
    bot.run()
