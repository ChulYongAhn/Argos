"""MinCoinBot state 초기화"""

import json
import os

STATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")

initial_state = {
    "balance": 10000000,
    "holding_qty": 0.0,
    "holding_avg_price": 0.0,
    "total_buy_amount": 0.0,
    "is_first_candle": True,
    "total_realized_profit": 0
}

with open(STATE_PATH, "w") as f:
    json.dump(initial_state, f, indent=2, ensure_ascii=False)

print("MinCoinBot 초기화 완료 (잔고: 10,000,000원)")
