"""
MinCoinBot - 업비트 BTC/KRW 5분봉 기반 가상 매매 시뮬레이션 봇
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
        self.logger.info("MinCoinBot 초기화 완료")
        self.logger.info(f"설정: 봉간격={self.config['candle_interval']}분, "
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

    def get_candle_data(self) -> dict:
        """업비트 API로 BTC/KRW 직전 봉 데이터 조회"""
        url = f"https://api.upbit.com/v1/candles/minutes/{self.config['candle_interval']}"
        params = {"market": "KRW-BTC", "count": 2}
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

    def calculate_profit_rate(self, current_price: float) -> float:
        """평단 대비 수익률(%) 계산"""
        avg_price = self.state["holding_avg_price"]
        if avg_price <= 0:
            return 0.0
        return (current_price - avg_price) / avg_price * 100

    def virtual_buy(self, current_price: float):
        """가상 매수 (buy_amount원어치)"""
        buy_amount = self.config["buy_amount"]

        # 잔고 부족 체크
        if self.state["balance"] < buy_amount:
            self.logger.warning(f"잔고 부족! 잔고={self.state['balance']:,.0f}원, 필요={buy_amount:,}원")
            return

        # 수수료 차감 후 실투자금
        fee = buy_amount * (self.config["buy_fee_rate"] / 100)
        actual_invest = buy_amount - fee
        buy_qty = actual_invest / current_price

        # 평단 재계산 (가중평균)
        prev_qty = self.state["holding_qty"]
        prev_total = self.state["total_buy_amount"]
        new_qty = prev_qty + buy_qty
        new_total = prev_total + buy_amount

        if new_qty > 0:
            self.state["holding_avg_price"] = (prev_qty * self.state["holding_avg_price"] + actual_invest) / new_qty
        self.state["holding_qty"] = new_qty
        self.state["total_buy_amount"] = new_total
        self.state["balance"] -= buy_amount

        self.logger.info(
            f"[매수] 가격={current_price:,.0f}원 | "
            f"수량={buy_qty:.8f}BTC | 수수료={fee:.1f}원 | "
            f"평단={self.state['holding_avg_price']:,.0f}원 | "
            f"총보유={new_qty:.8f}BTC | 잔고={self.state['balance']:,.0f}원"
        )

        # 구글시트 기록
        now = datetime.now()
        eval_amount = self.state["balance"] + (new_qty * current_price)
        profit_rate = self.calculate_profit_rate(current_price)
        self.write_sheet(
            now, "BTC", current_price,
            buy_amount, 0,
            eval_amount, self.state["balance"], new_total, profit_rate,
            self.state.get("total_realized_profit", 0)
        )

    def virtual_sell(self, current_price: float, reason: str):
        """가상 전량 매도"""
        holding_qty = self.state["holding_qty"]
        total_buy_amount = self.state["total_buy_amount"]

        # 매도 금액 및 수수료
        gross_sell = holding_qty * current_price
        fee = gross_sell * (self.config["sell_fee_rate"] / 100)
        net_sell = gross_sell - fee

        # 손익 계산
        profit = net_sell - total_buy_amount
        profit_rate = self.calculate_profit_rate(current_price)

        # 잔고 반영
        self.state["balance"] += net_sell
        self.state["total_realized_profit"] = self.state.get("total_realized_profit", 0) + profit

        self.logger.info(
            f"[{reason}] 가격={current_price:,.0f}원 | "
            f"매도금={net_sell:,.0f}원 | 수수료={fee:.1f}원 | "
            f"손익={profit:+,.0f}원 ({profit_rate:+.2f}%) | "
            f"누적실현익={self.state['total_realized_profit']:+,.0f}원 | "
            f"잔고={self.state['balance']:,.0f}원"
        )

        # 구글시트 기록
        now = datetime.now()
        self.write_sheet(
            now, "BTC", current_price,
            0, net_sell,
            self.state["balance"], self.state["balance"], 0, profit_rate,
            self.state["total_realized_profit"]
        )

        # 슬랙 알림
        self.slack.send(
            f"[Argos-MinCoinBot] BTC {reason} | "
            f"수익률: {profit_rate:+.2f}% | "
            f"수익금: {profit:+,.0f}원 | "
            f"누적실현익: {self.state['total_realized_profit']:+,.0f}원"
        )

        # state 리셋 → 다시 첫 봉부터
        self.state["holding_qty"] = 0.0
        self.state["holding_avg_price"] = 0.0
        self.state["total_buy_amount"] = 0.0
        self.state["is_first_candle"] = True

    def write_sheet(self, now: datetime, symbol: str, current_price: float,
                     buy_amount: float, sell_amount: float,
                     eval_amount: float, cash: float, invest_amount: float,
                     profit_rate: float, realized_profit: float):
        """구글시트 기록 (날짜/시간/종목이름/현재가/매수액/매도액/총평가액/현금/투자금액/수익률/누적실현익)"""
        sheet_name = os.getenv("GOOGLE_SHEET_NAME_1", "시트1")
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
                str(int(realized_profit)),
            )
        except Exception as e:
            self.logger.error(f"구글시트 기록 실패: {e}")

    def run(self):
        """메인 실행 루프"""
        interval_sec = self.config["candle_interval"] * 60
        self.logger.info(f"MinCoinBot 시작 (매 {self.config['candle_interval']}분 봉 기준)")

        while True:
            try:
                candle = self.get_candle_data()
                current_price = candle["current_price"]

                if self.state["is_first_candle"]:
                    # 첫 봉: 무조건 매수
                    self.logger.info(f"--- 첫 봉 진입 (BTC 현재가: {current_price:,.0f}원) ---")
                    self.virtual_buy(current_price)
                    self.state["is_first_candle"] = False
                else:
                    # 두 번째 봉부터: 봉 패턴 기반 판단
                    profit_rate = self.calculate_profit_rate(current_price)
                    avg_price = self.state["holding_avg_price"]
                    candle_type = "음봉" if candle["is_prev_bearish"] else "양봉"

                    self.logger.info(
                        f"현재가={current_price:,.0f}원 | "
                        f"평단={avg_price:,.0f}원 | "
                        f"수익률={profit_rate:+.2f}% | "
                        f"직전봉={candle_type}"
                    )

                    # 익절 조건: 수익률 ≥ +1.5% AND 직전 봉이 양봉
                    if profit_rate >= self.config["take_profit_rate"] and candle["is_prev_bullish"]:
                        self.virtual_sell(current_price, "익절")

                    # 매수 조건: 직전 봉이 음봉 AND 현재가 < 평단
                    elif candle["is_prev_bearish"] and current_price < avg_price:
                        self.virtual_buy(current_price)

                    else:
                        self.logger.info("[대기] 매매 조건 미충족")

                self.save_state()
                time.sleep(interval_sec)

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
