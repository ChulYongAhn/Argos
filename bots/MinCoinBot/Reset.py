"""MinCoinBot state 초기화 (config.json의 symbols 기반)"""

import json
import os

BOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BOT_DIR, "config.json")
STATE_PATH = os.path.join(BOT_DIR, "state.json")

with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

symbols = config.get("symbols", ["BTC"])

initial_state = {
    "balance": 10000000,
    "total_realized_profit": 0,
    "symbols": {}
}

for symbol in symbols:
    initial_state["symbols"][symbol] = {
        "holding_qty": 0.0,
        "holding_avg_price": 0.0,
        "total_buy_amount": 0.0,
        "is_first_candle": True,
    }

with open(STATE_PATH, "w") as f:
    json.dump(initial_state, f, indent=2, ensure_ascii=False)

print(f"MinCoinBot 초기화 완료 (잔고: 10,000,000원, 종목: {', '.join(symbols)})")
