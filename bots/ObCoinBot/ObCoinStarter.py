"""
ObCoin Trading Bot - SMC 기반 비트코인 24시간 자동매매 봇
Based on Smart Money Concept (Order Blocks, FVG, Liquidity Sweep)
"""

import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import json
import logging
from typing import Dict, List, Tuple, Optional
import os
import sys
from dataclasses import dataclass, asdict

# 상위 디렉토리 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.SlackService.simple_slack import SimpleSlack

# ==================== 설정 클래스 ====================
@dataclass
class TradingConfig:
    """트레이딩 설정"""
    # API 설정
    api_key: str = ""
    api_secret: str = ""

    # 매매 설정
    symbol: str = "BTC/USDT:USDT"  # 바이비트 선물
    leverage: int = 1  # 레버리지 사용 안함 (현물과 동일)
    position_size_percent: float = 0.9  # 총 자산의 90%
    max_positions: int = 1  # 최대 포지션 수

    # 타임프레임 설정 (멀티 타임프레임 분석)
    timeframes: Dict[str, str] = None

    # 리스크 관리
    max_loss_per_trade: float = 0.02  # 거래당 최대 손실 2%
    take_profit_ratio: float = 2.0  # 손익비 1:2
    trailing_stop: bool = True
    trailing_stop_percent: float = 0.01  # 1% 트레일링 스탑

    # SMC 분석 파라미터
    ob_min_body_ratio: float = 1.4  # 오더블럭 최소 몸통 비율 (30% 차이면 충분)
    fvg_min_gap_size: float = 0.0005  # FVG 최소 갭 크기 (0.05% - 작은 갭도 유효)
    min_confluence_count: int = 3  # 최소 근거 개수 (3개 유지 - SMC 원칙 고수)

    # 시스템 설정
    loop_interval: int = 60  # 메인 루프 간격 (초)
    debug_mode: bool = False

    def __post_init__(self):
        if self.timeframes is None:
            self.timeframes = {
                "htf": "4h",   # Higher Time Frame
                "mtf": "1h",   # Medium Time Frame
                "ltf": "15m"   # Lower Time Frame (진입용)
            }

# ==================== SMC 분석 엔진 ====================
class SMCAnalyzer:
    """Smart Money Concept 분석 엔진"""

    def __init__(self, config: TradingConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def detect_order_blocks(self, df: pd.DataFrame, bullish: bool = True) -> List[Dict]:
        """
        오더블럭 탐지
        bullish: True = 상승 오더블럭, False = 하락 오더블럭
        """
        order_blocks = []

        for i in range(2, len(df) - 1):
            if bullish:
                # 상승 오더블럭: [음봉] → [양봉(장대)]
                if (df['close'].iloc[i] > df['open'].iloc[i] and  # 현재 양봉
                    df['close'].iloc[i-1] < df['open'].iloc[i-1] and  # 이전 음봉
                    df['close'].iloc[i] > df['open'].iloc[i-1]):  # 반전 확인

                    # 몸통 크기 비율 확인
                    current_body = abs(df['close'].iloc[i] - df['open'].iloc[i])
                    prev_body = abs(df['close'].iloc[i-1] - df['open'].iloc[i-1])

                    if prev_body > 0 and current_body / prev_body >= self.config.ob_min_body_ratio:
                        ob = {
                            'type': 'bullish_ob',
                            'top': df['close'].iloc[i-1],
                            'bottom': df['open'].iloc[i-1],
                            'time': df.index[i-1],
                            'strength': current_body / prev_body,
                            'touched': False
                        }
                        order_blocks.append(ob)
            else:
                # 하락 오더블럭: [양봉] → [음봉(장대)]
                if (df['close'].iloc[i] < df['open'].iloc[i] and  # 현재 음봉
                    df['close'].iloc[i-1] > df['open'].iloc[i-1] and  # 이전 양봉
                    df['close'].iloc[i] < df['open'].iloc[i-1]):  # 반전 확인

                    # 몸통 크기 비율 확인
                    current_body = abs(df['open'].iloc[i] - df['close'].iloc[i])
                    prev_body = abs(df['close'].iloc[i-1] - df['open'].iloc[i-1])

                    if prev_body > 0 and current_body / prev_body >= self.config.ob_min_body_ratio:
                        ob = {
                            'type': 'bearish_ob',
                            'top': df['open'].iloc[i-1],
                            'bottom': df['close'].iloc[i-1],
                            'time': df.index[i-1],
                            'strength': current_body / prev_body,
                            'touched': False
                        }
                        order_blocks.append(ob)

        return order_blocks

    def detect_fvg(self, df: pd.DataFrame, bullish: bool = True) -> List[Dict]:
        """
        Fair Value Gap 탐지
        bullish: True = 상승 FVG, False = 하락 FVG
        """
        fvgs = []

        for i in range(2, len(df)):
            if bullish:
                # 상승 FVG: 1번 캔들 고가와 3번 캔들 저가 사이 갭
                gap_top = df['low'].iloc[i]
                gap_bottom = df['high'].iloc[i-2]

                if gap_top > gap_bottom:
                    gap_size = (gap_top - gap_bottom) / gap_bottom
                    if gap_size >= self.config.fvg_min_gap_size:
                        fvg = {
                            'type': 'bullish_fvg',
                            'top': gap_top,
                            'bottom': gap_bottom,
                            'time': df.index[i-1],
                            'size': gap_size,
                            'filled': False
                        }
                        fvgs.append(fvg)
            else:
                # 하락 FVG: 1번 캔들 저가와 3번 캔들 고가 사이 갭
                gap_top = df['low'].iloc[i-2]
                gap_bottom = df['high'].iloc[i]

                if gap_top > gap_bottom:
                    gap_size = (gap_top - gap_bottom) / gap_bottom
                    if gap_size >= self.config.fvg_min_gap_size:
                        fvg = {
                            'type': 'bearish_fvg',
                            'top': gap_top,
                            'bottom': gap_bottom,
                            'time': df.index[i-1],
                            'size': gap_size,
                            'filled': False
                        }
                        fvgs.append(fvg)

        return fvgs

    def detect_liquidity_sweep(self, df: pd.DataFrame, lookback: int = 20) -> List[Dict]:
        """
        유동성 스윕 탐지 (스탑 헌팅)
        """
        sweeps = []

        for i in range(lookback, len(df)):
            window = df.iloc[i-lookback:i]

            # 스윙 하이/로우 찾기
            swing_high = window['high'].max()
            swing_low = window['low'].min()

            current_high = df['high'].iloc[i]
            current_low = df['low'].iloc[i]
            current_close = df['close'].iloc[i]

            # 상방 유동성 스윕 (고점 돌파 후 하락)
            if current_high > swing_high and current_close < swing_high:
                sweep = {
                    'type': 'bullish_sweep',  # 매수 기회
                    'level': swing_high,
                    'time': df.index[i],
                    'wick_size': (current_high - current_close) / current_close
                }
                sweeps.append(sweep)

            # 하방 유동성 스윕 (저점 돌파 후 상승)
            if current_low < swing_low and current_close > swing_low:
                sweep = {
                    'type': 'bearish_sweep',  # 매도 기회
                    'level': swing_low,
                    'time': df.index[i],
                    'wick_size': (current_close - current_low) / current_low
                }
                sweeps.append(sweep)

        return sweeps

    def calculate_market_structure(self, df: pd.DataFrame) -> Dict:
        """
        시장 구조 분석 (추세 파악)
        """
        # 최근 고점/저점 찾기
        window = 50
        highs = []
        lows = []

        for i in range(window, len(df) - window):
            # 로컬 고점
            if df['high'].iloc[i] == df['high'].iloc[i-window:i+window].max():
                highs.append({'price': df['high'].iloc[i], 'index': i})
            # 로컬 저점
            if df['low'].iloc[i] == df['low'].iloc[i-window:i+window].min():
                lows.append({'price': df['low'].iloc[i], 'index': i})

        # 추세 판단
        trend = 'neutral'
        if len(highs) >= 2 and len(lows) >= 2:
            # HH-HL: 상승 추세
            if (highs[-1]['price'] > highs[-2]['price'] and
                lows[-1]['price'] > lows[-2]['price']):
                trend = 'bullish'
            # LH-LL: 하락 추세
            elif (highs[-1]['price'] < highs[-2]['price'] and
                  lows[-1]['price'] < lows[-2]['price']):
                trend = 'bearish'

        return {
            'trend': trend,
            'highs': highs[-3:] if highs else [],
            'lows': lows[-3:] if lows else [],
            'last_swing_high': highs[-1]['price'] if highs else None,
            'last_swing_low': lows[-1]['price'] if lows else None
        }

# ==================== 트레이딩 봇 메인 클래스 ====================
class ObCoinBot:
    """ObCoin Trading Bot 메인 클래스"""

    def __init__(self, config: TradingConfig):
        self.config = config
        self.setup_logging()
        self.logger = logging.getLogger(__name__)

        # Bybit 거래소 연결
        self.exchange = self.connect_exchange()

        # SMC 분석기
        self.analyzer = SMCAnalyzer(config)

        # Slack 서비스 (알림용)
        try:
            self.slack = SimpleSlack()
        except:
            self.slack = None
            self.logger.warning("Slack 서비스를 초기화할 수 없습니다")

        # 상태 관리
        self.position = None
        self.orders = []
        self.trade_history = []
        self.analysis_cache = {}

        # 알림 제한
        self.last_notification = {}  # 마지막 알림 시간 저장
        self.notification_cooldown = 3600  # 같은 알림 1시간 쿨다운

        # 기존 포지션 동기화
        self.sync_position_from_exchange()

        self.logger.info("ObCoin Bot 초기화 완료")

    def setup_logging(self):
        """로깅 설정"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        log_level = logging.DEBUG if self.config.debug_mode else logging.INFO

        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler(f'obcoin_bot_{datetime.now().strftime("%Y%m%d")}.log'),
                logging.StreamHandler()
            ]
        )

    def connect_exchange(self) -> ccxt.bybit:
        """Bybit 거래소 연결"""
        exchange = ccxt.bybit({
            'apiKey': self.config.api_key,
            'secret': self.config.api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'swap',  # 무기한 선물
            }
        })

        # 테스트넷 사용 (실거래 전 테스트)
        if self.config.debug_mode:
            exchange.set_sandbox_mode(True)

        return exchange

    def sync_position_from_exchange(self):
        """거래소에서 실제 포지션 정보 가져와서 동기화"""
        try:
            self.logger.info("기존 포지션 확인 중...")

            # 바이비트에서 현재 포지션 조회
            positions = self.exchange.fetch_positions([self.config.symbol])

            if positions and len(positions) > 0:
                pos = positions[0]

                # 포지션이 있는 경우
                if pos['contracts'] > 0:
                    self.logger.info(f"기존 포지션 발견: {pos['side']} {pos['contracts']} BTC")

                    # 포지션 정보 복원
                    self.position = {
                        'side': pos['side'].upper(),  # 'long' -> 'BUY', 'short' -> 'SELL'
                        'entry_price': pos['info'].get('avg_price', pos['markPrice']),
                        'size': pos['contracts'],
                        'stop_loss': None,  # 스탑 주문은 별도 조회 필요
                        'take_profit': None,
                        'timestamp': datetime.now(),
                        'pnl_percent': pos['percentage'],
                        'unrealized_pnl': pos['unrealizedPnl'],
                        'mark_price': pos['markPrice']
                    }

                    # 스탑/익절 주문 조회
                    open_orders = self.exchange.fetch_open_orders(self.config.symbol)
                    for order in open_orders:
                        if order['type'] == 'stop_loss':
                            self.position['stop_loss'] = order['price']
                            self.position['stop_order_id'] = order['id']
                        elif order['type'] == 'take_profit':
                            self.position['take_profit'] = order['price']
                            self.position['tp_order_id'] = order['id']

                    # 상태 알림
                    message = f"""
                    📊 **기존 포지션 감지**
                    - 방향: {self.position['side']}
                    - 진입가: ${self.position['entry_price']:.2f}
                    - 현재가: ${self.position['mark_price']:.2f}
                    - 수량: {self.position['size']:.4f} BTC
                    - PnL: {self.position['pnl_percent']:.2f}%
                    - 미실현 손익: ${self.position['unrealized_pnl']:.2f}
                    """

                    if self.slack:
                        self.slack.send(f"[Argos-ObCoin] {message}")

                    self.logger.info(f"포지션 복원 완료 - PnL: {self.position['pnl_percent']:.2f}%")
                else:
                    self.logger.info("활성 포지션 없음")
                    self.position = None
            else:
                self.logger.info("활성 포지션 없음")
                self.position = None

        except Exception as e:
            self.logger.error(f"포지션 동기화 실패: {e}")
            self.position = None

    def fetch_ohlcv_multi_timeframe(self) -> Dict[str, pd.DataFrame]:
        """멀티 타임프레임 OHLCV 데이터 가져오기"""
        data = {}

        for tf_name, timeframe in self.config.timeframes.items():
            try:
                ohlcv = self.exchange.fetch_ohlcv(
                    self.config.symbol,
                    timeframe,
                    limit=200
                )

                df = pd.DataFrame(
                    ohlcv,
                    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                )
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)

                data[tf_name] = df

            except Exception as e:
                self.logger.error(f"OHLCV 데이터 가져오기 실패 ({timeframe}): {e}")

        return data

    def analyze_market(self) -> Dict:
        """시장 분석 - SMC 기반"""
        analysis = {
            'timestamp': datetime.now(),
            'signals': [],
            'confluence_count': 0,
            'recommendation': 'WAIT'
        }

        try:
            # 멀티 타임프레임 데이터 가져오기
            mt_data = self.fetch_ohlcv_multi_timeframe()

            if not mt_data:
                return analysis

            # 상위 타임프레임 분석 (큰 그림)
            htf_df = mt_data.get('htf')
            if htf_df is not None:
                # 시장 구조
                market_structure = self.analyzer.calculate_market_structure(htf_df)
                analysis['market_structure'] = market_structure

                # HTF 오더블럭
                htf_bullish_obs = self.analyzer.detect_order_blocks(htf_df, bullish=True)
                htf_bearish_obs = self.analyzer.detect_order_blocks(htf_df, bullish=False)

                analysis['htf_order_blocks'] = {
                    'bullish': htf_bullish_obs[-3:] if htf_bullish_obs else [],
                    'bearish': htf_bearish_obs[-3:] if htf_bearish_obs else []
                }

            # 하위 타임프레임 분석 (진입 타이밍)
            ltf_df = mt_data.get('ltf')
            if ltf_df is not None:
                current_price = ltf_df['close'].iloc[-1]

                # 오더블럭 탐지
                bullish_obs = self.analyzer.detect_order_blocks(ltf_df, bullish=True)
                bearish_obs = self.analyzer.detect_order_blocks(ltf_df, bullish=False)

                # FVG 탐지
                bullish_fvgs = self.analyzer.detect_fvg(ltf_df, bullish=True)
                bearish_fvgs = self.analyzer.detect_fvg(ltf_df, bullish=False)

                # 유동성 스윕 탐지
                liquidity_sweeps = self.analyzer.detect_liquidity_sweep(ltf_df)

                # 매수 신호 체크
                buy_signals = []

                # 1. 상승 추세 확인
                if market_structure.get('trend') == 'bullish':
                    buy_signals.append('BULLISH_TREND')

                # 2. 유동성 스윕 발생
                recent_sweeps = [s for s in liquidity_sweeps if s['type'] == 'bullish_sweep']
                if recent_sweeps and len(recent_sweeps) > 0:
                    last_sweep_time = recent_sweeps[-1]['time']
                    if (datetime.now() - last_sweep_time).total_seconds() < 3600:  # 1시간 이내
                        buy_signals.append('LIQUIDITY_SWEEP')

                # 3. 오더블럭 터치
                for ob in bullish_obs[-5:]:  # 최근 5개만 체크
                    if ob['bottom'] <= current_price <= ob['top'] and not ob['touched']:
                        buy_signals.append('BULLISH_OB_TOUCH')
                        ob['touched'] = True
                        break

                # 4. FVG 진입
                for fvg in bullish_fvgs[-5:]:  # 최근 5개만 체크
                    if fvg['bottom'] <= current_price <= fvg['top'] and not fvg['filled']:
                        buy_signals.append('BULLISH_FVG_ENTRY')
                        fvg['filled'] = True
                        break

                # 매도 신호 체크 (숏 포지션용)
                sell_signals = []

                # 1. 하락 추세 확인
                if market_structure.get('trend') == 'bearish':
                    sell_signals.append('BEARISH_TREND')

                # 2. 하락 오더블럭 터치
                for ob in bearish_obs[-5:]:
                    if ob['bottom'] <= current_price <= ob['top'] and not ob['touched']:
                        sell_signals.append('BEARISH_OB_TOUCH')
                        ob['touched'] = True
                        break

                # 분석 결과 저장
                analysis['buy_signals'] = buy_signals
                analysis['sell_signals'] = sell_signals
                analysis['confluence_count'] = max(len(buy_signals), len(sell_signals))

                # 최종 추천
                if len(buy_signals) >= self.config.min_confluence_count:
                    analysis['recommendation'] = 'BUY'
                    analysis['entry_price'] = current_price
                    analysis['stop_loss'] = current_price * 0.98  # 2% 손절
                    analysis['take_profit'] = current_price * 1.04  # 4% 익절
                elif len(sell_signals) >= self.config.min_confluence_count:
                    analysis['recommendation'] = 'SELL'
                    analysis['entry_price'] = current_price
                    analysis['stop_loss'] = current_price * 1.02
                    analysis['take_profit'] = current_price * 0.96

                # 분석 정보 저장
                analysis.update({
                    'current_price': current_price,
                    'order_blocks': {'bullish': bullish_obs[-3:], 'bearish': bearish_obs[-3:]},
                    'fvgs': {'bullish': bullish_fvgs[-3:], 'bearish': bearish_fvgs[-3:]},
                    'liquidity_sweeps': liquidity_sweeps[-3:]
                })

        except Exception as e:
            self.logger.error(f"시장 분석 실패: {e}")

        return analysis

    def execute_trade(self, signal: str, analysis: Dict) -> bool:
        """거래 실행"""
        try:
            # 이미 포지션이 있는지 확인
            if self.position is not None:
                self.logger.info("이미 포지션이 있습니다")
                return False

            # 잔고 확인
            balance = self.exchange.fetch_balance()
            usdt_balance = balance['USDT']['free']

            # 최소 거래 금액 체크 (10 USDT)
            if usdt_balance < 10:
                # 1시간에 한 번만 알림
                current_time = datetime.now()
                last_balance_warning = self.last_notification.get('low_balance', datetime.min)

                if (current_time - last_balance_warning).total_seconds() > self.notification_cooldown:
                    self.logger.warning(f"잔고 부족: ${usdt_balance:.2f}")
                    if self.slack:
                        self.slack.send(f"[Argos-ObCoin] ⚠️ 잔고 부족: ${usdt_balance:.2f}")
                    self.last_notification['low_balance'] = current_time
                return False

            # 포지션 사이즈 계산
            position_size = usdt_balance * self.config.position_size_percent
            btc_amount = position_size / analysis['current_price']

            # 레버리지 설정
            self.exchange.set_leverage(self.config.leverage, self.config.symbol)

            # 주문 실행
            if signal == 'BUY':
                order = self.exchange.create_market_order(
                    self.config.symbol,
                    'buy',
                    btc_amount
                )

                # 손절/익절 주문
                self.exchange.create_order(
                    self.config.symbol,
                    'stop_loss',
                    'sell',
                    btc_amount,
                    analysis['stop_loss']
                )

                self.exchange.create_order(
                    self.config.symbol,
                    'take_profit',
                    'sell',
                    btc_amount,
                    analysis['take_profit']
                )

            elif signal == 'SELL':
                order = self.exchange.create_market_order(
                    self.config.symbol,
                    'sell',
                    btc_amount
                )

                # 손절/익절 주문
                self.exchange.create_order(
                    self.config.symbol,
                    'stop_loss',
                    'buy',
                    btc_amount,
                    analysis['stop_loss']
                )

                self.exchange.create_order(
                    self.config.symbol,
                    'take_profit',
                    'buy',
                    btc_amount,
                    analysis['take_profit']
                )

            # 포지션 정보 저장
            self.position = {
                'side': signal,
                'entry_price': analysis['entry_price'],
                'size': btc_amount,
                'stop_loss': analysis['stop_loss'],
                'take_profit': analysis['take_profit'],
                'timestamp': datetime.now(),
                'analysis': analysis
            }

            # 알림 전송
            message = f"""
            🚀 **포지션 오픈**
            - 방향: {signal}
            - 진입가: ${analysis['entry_price']:.2f}
            - 수량: {btc_amount:.4f} BTC
            - 손절: ${analysis['stop_loss']:.2f}
            - 익절: ${analysis['take_profit']:.2f}
            - 근거: {', '.join(analysis.get('buy_signals', []) or analysis.get('sell_signals', []))}
            """

            if self.slack:
                self.slack.send(f"[Argos-ObCoin] {message}")

            self.logger.info(f"거래 실행 완료: {order}")
            return True

        except Exception as e:
            self.logger.error(f"거래 실행 실패: {e}")
            return False

    def check_position_status(self):
        """포지션 상태 확인 및 관리"""
        try:
            # 현재 포지션 조회 (항상 실제 거래소 정보 기준)
            positions = self.exchange.fetch_positions([self.config.symbol])

            if not positions or positions[0]['contracts'] == 0:
                # 포지션이 청산됨
                if self.position is not None:
                    self.logger.info("포지션이 청산되었습니다")

                    # 청산 알림
                    if self.slack:
                        self.slack.send("[Argos-ObCoin] ✅ 포지션 청산 완료")

                self.position = None
                return

            # 포지션이 있는 경우
            current_position = positions[0]
            current_price = current_position['markPrice']
            pnl_percent = current_position['percentage']

            # 포지션 정보 업데이트
            if self.position is None:
                # 봇 재시작 후 처음 감지된 경우
                self.sync_position_from_exchange()
            else:
                # 기존 포지션 업데이트
                self.position['mark_price'] = current_price
                self.position['pnl_percent'] = pnl_percent
                self.position['unrealized_pnl'] = current_position['unrealizedPnl']

            # 트레일링 스탑 업데이트
            if self.config.trailing_stop and pnl_percent > 2:  # 2% 이상 수익
                side = 'LONG' if current_position['side'] == 'long' else 'SHORT'

                if side == 'LONG' and self.position.get('stop_loss'):
                    new_stop = current_price * (1 - self.config.trailing_stop_percent)
                    if new_stop > self.position['stop_loss']:
                        # 스탑로스 업데이트
                        if 'stop_order_id' in self.position:
                            self.exchange.edit_order(
                                self.position['stop_order_id'],
                                self.config.symbol,
                                'stop_loss',
                                'sell',
                                self.position['size'],
                                new_stop
                            )
                            self.position['stop_loss'] = new_stop
                            self.logger.info(f"트레일링 스탑 업데이트: ${new_stop:.2f}")

                            # 트레일링 스탑 알림 (하루 최대 1번)
                            current_time = datetime.now()
                            last_trail_notify = self.last_notification.get('trailing_stop', datetime.min)
                            if (current_time - last_trail_notify).total_seconds() > 86400:  # 24시간
                                if self.slack:
                                    self.slack.send(f"[Argos-ObCoin] 📈 트레일링 스탑 업데이트: ${new_stop:.2f} (PnL: +{pnl_percent:.2f}%)")
                                self.last_notification['trailing_stop'] = current_time

        except Exception as e:
            self.logger.error(f"포지션 상태 확인 실패: {e}")

    def send_status_report(self):
        """정기 상태 리포트 전송 (6시간마다)"""
        try:
            balance = self.exchange.fetch_balance()
            usdt_balance = balance.get('USDT', {}).get('total', 0)

            status_msg = f"""
[Argos-ObCoin] 📊 정기 상태 리포트

💰 잔고: ${usdt_balance:.2f}
📈 포지션: {'있음' if self.position else '없음'}
"""

            if self.position:
                status_msg += f"""
- 방향: {self.position.get('side', 'N/A')}
- PnL: {self.position.get('pnl_percent', 0):.2f}%
- 미실현 손익: ${self.position.get('unrealized_pnl', 0):.2f}
"""

            status_msg += f"""
⏰ 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
✅ 봇 정상 작동 중
"""

            if self.slack:
                self.slack.send(status_msg)

        except Exception as e:
            self.logger.error(f"상태 리포트 전송 실패: {e}")

    def run(self):
        """메인 실행 루프"""
        self.logger.info("ObCoin Bot 시작")

        if self.slack:
            self.slack.send("[Argos-ObCoin] 🤖 ObCoin Bot 가동 시작")

        loop_count = 0
        while True:
            try:
                loop_count += 1

                # 1. 시장 분석 (매 루프)
                self.logger.debug(f"루프 #{loop_count}: 시장 분석 중...")
                analysis = self.analyze_market()

                # 2. 포지션 확인
                self.check_position_status()

                # 3. 거래 신호 확인 및 실행
                if self.position is None:  # 포지션이 없을 때만
                    if analysis['recommendation'] in ['BUY', 'SELL']:
                        self.logger.info(f"거래 신호 감지: {analysis['recommendation']}")
                        self.logger.info(f"근거 수: {analysis['confluence_count']}")

                        # 거래 실행
                        success = self.execute_trade(
                            analysis['recommendation'],
                            analysis
                        )

                        if success:
                            self.logger.info("거래 실행 성공")
                        else:
                            self.logger.debug("거래 실행 조건 미충족")
                else:
                    self.logger.debug(f"포지션 보유 중... PnL: {self.position.get('pnl_percent', 0):.2f}%")

                # 4. 정기 상태 리포트 (6시간마다)
                if loop_count % 360 == 0:  # 60초 * 360 = 6시간
                    self.send_status_report()

                # 5. 대기 (debug 모드가 아니면 상세 로그 생략)
                if not self.config.debug_mode:
                    time.sleep(self.config.loop_interval)
                else:
                    self.logger.info(f"{self.config.loop_interval}초 대기...")
                    time.sleep(self.config.loop_interval)

            except KeyboardInterrupt:
                self.logger.info("사용자 중단 요청")
                break
            except Exception as e:
                self.logger.error(f"메인 루프 오류: {e}")
                time.sleep(10)

        self.logger.info("ObCoin Bot 종료")

# ==================== 실행 ====================
def main():
    """메인 실행 함수"""

    # 설정 로드
    config = TradingConfig(
        api_key=os.getenv("BYBIT_API_KEY", ""),
        api_secret=os.getenv("BYBIT_API_SECRET", ""),
        debug_mode=False  # 실거래 모드
    )

    # 봇 생성 및 실행
    bot = ObCoinBot(config)

    try:
        bot.run()
    except Exception as e:
        logging.error(f"봇 실행 중 오류 발생: {e}")
        if bot.slack:
            bot.slack.send(f"[Argos-ObCoin] ❌ 봇 오류: {e}")

if __name__ == "__main__":
    main()