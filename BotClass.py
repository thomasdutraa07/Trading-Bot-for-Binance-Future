from ta.momentum import stochrsi_d, stochrsi_k, stoch, stoch_signal, rsi
from ta.trend import ema_indicator, macd_signal, macd, sma_indicator
from ta.volatility import average_true_range, bollinger_pband
import pandas as pd, sys, os
import TradingStrats as TS
from Logger import *
from LiveTradingConfig import custom_tp_sl_functions, wait_for_candle_close

class Bot:
    def __init__(self, symbol, Open, Close, High, Low, Volume, Date, OP, CP, index, tick,
                 strategy, TP_SL_choice, SL_mult, TP_mult, backtesting=0, signal_queue=None, print_trades_q=None):
        self.symbol, self.Date = symbol, Date
        n = min(len(Open), len(Close), len(High), len(Low), len(Volume))
        self.Open, self.Close, self.High, self.Low, self.Volume = Open[-n:], Close[-n:], High[-n:], Low[-n:], Volume[-n:]
        self.OP, self.CP, self.index, self.tick_size = OP, CP, index, tick
        self.add_hist_complete = 0
        self.Open_H, self.Close_H, self.High_H, self.Low_H = [], [], [], []
        self.socket_failed = False
        self.backtesting = backtesting
        self.use_close_pos = False
        self.strategy = strategy
        self.TP_SL_choice, self.SL_mult, self.TP_mult = TP_SL_choice, SL_mult, TP_mult
        self.indicators, self.current_index = {}, -1
        self.take_profit_val, self.stop_loss_val = [], []
        self.peaks, self.troughs = [], []
        self.signal_queue = signal_queue
        if self.index == 0: self.print_trades_q = print_trades_q
        if backtesting:
            self.add_hist([], [], [], [], [], [])
            self.update_indicators()
            self.update_TP_SL()
        self.first_interval = False
        self.pop_previous_value = False

    def _series(self):
        C = pd.Series(self.Close)
        H = pd.Series(self.High)
        L = pd.Series(self.Low)
        V = pd.Series(self.Volume)
        return C, H, L, V

    def update_indicators(self):
        try:
            C, H, L, V = self._series()
            s = self.strategy
            if s == 'StochRSIMACD':
                self.indicators = {
                    "fastd": {"values": list(stoch(close=C, high=H, low=L)), "plotting_axis": 3},
                    "fastk": {"values": list(stoch_signal(close=C, high=H, low=L)), "plotting_axis": 3},
                    "RSI": {"values": list(rsi(C)), "plotting_axis": 4},
                    "MACD": {"values": list(macd(C)), "plotting_axis": 5},
                    "macdsignal": {"values": list(macd_signal(C)), "plotting_axis": 5},
                }
            elif s == 'tripleEMAStochasticRSIATR':
                self.indicators = {
                    "EMA_L": {"values": list(ema_indicator(C, window=100)), "plotting_axis": 1},
                    "EMA_M": {"values": list(ema_indicator(C, window=50)), "plotting_axis": 1},
                    "EMA_S": {"values": list(ema_indicator(C, window=20)), "plotting_axis": 1},
                    "fastd": {"values": list(stochrsi_d(C)), "plotting_axis": 3},
                    "fastk": {"values": list(stochrsi_k(C)), "plotting_axis": 3},
                }
            elif s == 'tripleEMA':
                self.indicators = {
                    "EMA_L": {"values": list(ema_indicator(C, window=50)), "plotting_axis": 1},
                    "EMA_M": {"values": list(ema_indicator(C, window=20)), "plotting_axis": 1},
                    "EMA_S": {"values": list(ema_indicator(C, window=5)), "plotting_axis": 1},
                }
            elif s == 'breakout':
                self.indicators = {
                    "max Close % change": {"values": list(C.rolling(10).max()), "plotting_axis": 3},
                    "min Close % change": {"values": list(C.rolling(10).min()), "plotting_axis": 3},
                    "max Volume": {"values": list(V.rolling(10).max()), "plotting_axis": 2},
                }
            elif s == 'stochBB':
                self.indicators = {
                    "fastd": {"values": list(stochrsi_d(C)), "plotting_axis": 3},
                    "fastk": {"values": list(stochrsi_k(C)), "plotting_axis": 3},
                    "percent_B": {"values": list(bollinger_pband(C)), "plotting_axis": 4},
                }
            elif s == 'goldenCross':
                self.indicators = {
                    "EMA_L": {"values": list(ema_indicator(C, window=100)), "plotting_axis": 1},
                    "EMA_M": {"values": list(ema_indicator(C, window=50)), "plotting_axis": 1},
                    "EMA_S": {"values": list(ema_indicator(C, window=20)), "plotting_axis": 1},
                    "RSI": {"values": list(rsi(C)), "plotting_axis": 3},
                }
            elif s == 'fibMACD':
                self.indicators = {
                    "MACD_signal": {"values": list(macd_signal(C)), "plotting_axis": 3},
                    "MACD": {"values": list(macd(C)), "plotting_axis": 3},
                    "EMA": {"values": list(sma_indicator(C, window=200)), "plotting_axis": 1},
                }
            elif s == 'EMA_cross':
                self.indicators = {
                    "EMA_S": {"values": list(ema_indicator(C, window=5)), "plotting_axis": 1},
                    "EMA_L": {"values": list(ema_indicator(C, window=20)), "plotting_axis": 1},
                }
            elif s in ('heikin_ashi_ema2', 'heikin_ashi_ema'):
                self.use_close_pos = True
                self.indicators = {
                    "fastd": {"values": list(stochrsi_d(C)), "plotting_axis": 3},
                    "fastk": {"values": list(stochrsi_k(C)), "plotting_axis": 3},
                    "EMA": {"values": list(ema_indicator(C, window=200)), "plotting_axis": 1},
                }
            elif s == 'ema_crossover':
                self.indicators = {
                    "ema_short": {"values": list(ema_indicator(C, window=20)), "plotting_axis": 1},
                    "ema_long": {"values": list(ema_indicator(C, window=50)), "plotting_axis": 1},
                }
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            log.error(f'update_indicators() - strategy: {self.strategy}, Info: {(exc_obj, fname, exc_tb.tb_lineno)}, Error: {e}')

    def _extrema(self, arr, level, peak=True):
        n = len(arr)
        out = [0]*n
        for i in range(n):
            if i < level or i > n - level - 1: continue
            ok = all((arr[i] > arr[i-k] and arr[i] > arr[i+k]) if peak else (arr[i] < arr[i-k] and arr[i] < arr[i+k]) for k in range(1, level+1))
            out[i] = arr[i] if ok else 0
        return out

    def update_TP_SL(self):
        try:
            c = self.TP_SL_choice
            if c == '%':
                self.take_profit_val = [(self.TP_mult/100)*p for p in self.Close]
                self.stop_loss_val = [(self.SL_mult/100)*p for p in self.Close]
            elif c == 'x (ATR)':
                atr = average_true_range(self.High, self.Low, self.Close)
                self.take_profit_val = [self.TP_mult*abs(a) for a in atr]
                self.stop_loss_val = [self.SL_mult*abs(a) for a in atr]
            elif c in ('x (Swing High/Low) level 1','x (Swing High/Low) level 2','x (Swing High/Low) level 3'):
                lvl = int(c[-1])
                self.peaks = self._extrema(self.High, lvl, True)
                self.troughs = self._extrema(self.Low,  lvl, False)
            elif c in ('x (Swing Close) level 1','x (Swing Close) level 2','x (Swing Close) level 3'):
                lvl = int(c[-1])
                self.peaks = self._extrema(self.Close, lvl, True)
                self.troughs = self._extrema(self.Close, lvl, False)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            log.error(f'update_TP_SL() - choice: {self.TP_SL_choice}, Info: {(exc_obj, fname, exc_tb.tb_lineno)}, Error: {e}')

    def add_hist(self, Date_temp, Open_temp, Close_temp, High_temp, Low_temp, Volume_temp):
        if not self.backtesting:
            try:
                while self.Date:
                    if self.Date[0] > Date_temp[-1]:
                        Date_temp.append(self.Date.pop(0)); Open_temp.append(self.Open.pop(0))
                        Close_temp.append(self.Close.pop(0)); High_temp.append(self.High.pop(0))
                        Low_temp.append(self.Low.pop(0)); Volume_temp.append(self.Volume.pop(0))
                    else:
                        self.Date.pop(0); self.Open.pop(0); self.Close.pop(0); self.High.pop(0); self.Low.pop(0); self.Volume.pop(0)
                self.Date, self.Open, self.Close, self.High, self.Low, self.Volume = Date_temp, Open_temp, Close_temp, High_temp, Low_temp, Volume_temp
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                log.error(f'add_hist() - merge error, Info: {(exc_obj, fname, exc_tb.tb_lineno)}, Error: {e}')
        try:
            self.Close_H.append((self.Open[0] + self.Close[0] + self.Low[0] + self.High[0]) / 4)
            self.Open_H.append((self.Close[0] + self.Open[0]) / 2)
            self.High_H.append(self.High[0]); self.Low_H.append(self.Low[0])
            for i in range(1, len(self.Close)):
                self.Open_H.append((self.Open_H[i-1] + self.Close_H[i-1]) / 2)
                self.Close_H.append((self.Open[i] + self.Close[i] + self.Low[i] + self.High[i]) / 4)
                self.High_H.append(max(self.High[i], self.Open_H[i], self.Close_H[i]))
                self.Low_H.append(min(self.Low[i], self.Open_H[i], self.Close_H[i]))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            log.error(f'add_hist() - heikin ashi error, Info: {(exc_obj, fname, exc_tb.tb_lineno)}, Error: {e}')
        self.add_hist_complete = 1

    def handle_socket_message(self, msg):
        try:
            if msg:
                k = msg['k']
                closed = k['x']
                if closed or (not wait_for_candle_close and self.first_interval and self.add_hist_complete):
                    if self.pop_previous_value: self.remove_last_candle()
                    self.pop_previous_value = not closed
                    self.consume_new_candle(k)
                    if self.add_hist_complete:
                        self.generate_new_heikin_ashi()
                        d, sl, tp = self.make_decision()
                        if d != -99:
                            self.signal_queue.put([self.symbol, self.OP, self.CP, self.tick_size, d, self.index, sl, tp])
                        if closed: self.remove_first_candle()
                    if self.index == 0: self.print_trades_q.put(True)
                    self.first_interval = True
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            log.warning(f"handle_socket_message() - {self.symbol} failed, msg: {msg}, Info: {(exc_obj, fname, exc_tb.tb_lineno)}, Error: {e}")
            self.socket_failed = True

    def make_decision(self):
        self.update_indicators()
        d, sl, tp = -99, -99, -99
        try:
            s = self.strategy
            if s == 'StochRSIMACD':
                d = TS.StochRSIMACD(d, self.indicators["fastd"]["values"], self.indicators["fastk"]["values"],
                                    self.indicators["RSI"]["values"], self.indicators["MACD"]["values"],
                                    self.indicators["macdsignal"]["values"], self.current_index)
            elif s == 'tripleEMAStochasticRSIATR':
                d = TS.tripleEMAStochasticRSIATR(self.Close, d, self.indicators["EMA_L"]["values"],
                                                 self.indicators["EMA_M"]["values"], self.indicators["EMA_S"]["values"],
                                                 self.indicators["fastd"]["values"], self.indicators["fastk"]["values"], self.current_index)
            elif s == 'tripleEMA':
                d = TS.tripleEMA(d, self.indicators["EMA_S"]["values"], self.indicators["EMA_M"]["values"],
                                 self.indicators["EMA_L"]["values"], self.current_index)
            elif s == 'breakout':
                d = TS.breakout(d, self.Close, self.Volume,
                                self.indicators["max Close % change"]["values"],
                                self.indicators["min Close % change"]["values"],
                                self.indicators["max Volume"]["values"], self.current_index)
            elif s == 'stochBB':
                d = TS.stochBB(d, self.indicators["fastd"]["values"], self.indicators["fastk"]["values"],
                               self.indicators["percent_B"]["values"], self.current_index)
            elif s == 'goldenCross':
                d = TS.goldenCross(d, self.Close, self.indicators["EMA_L"]["values"], self.indicators["EMA_M"]["values"],
                                   self.indicators["EMA_S"]["values"], self.indicators["RSI"]["values"], self.current_index)
            elif s == 'candle_wick':
                d = TS.candle_wick(d, self.Close, self.Open, self.High, self.Low, self.current_index)
            elif s == 'fibMACD':
                d = TS.fibMACD(d, self.Close, self.Open, self.High, self.Low,
                               self.indicators["MACD_signal"]["values"], self.indicators["MACD"]["values"],
                               self.indicators["EMA"]["values"], self.current_index)
            elif s == 'EMA_cross':
                d = TS.EMA_cross(d, self.indicators["EMA_S"]["values"], self.indicators["EMA_L"]["values"], self.current_index)
            elif s == 'heikin_ashi_ema2':
                d, _ = TS.heikin_ashi_ema2(self.Open_H, self.High_H, self.Low_H, self.Close_H, d, -99, 0,
                                           self.indicators["fastd"]["values"], self.indicators["fastk"]["values"],
                                           self.indicators["EMA"]["values"], self.current_index)
            elif s == 'heikin_ashi_ema':
                d, _ = TS.heikin_ashi_ema(self.Open_H, self.Close_H, d, -99, 0,
                                          self.indicators["fastd"]["values"], self.indicators["fastk"]["values"],
                                          self.indicators["EMA"]["values"], self.current_index)
            elif s == "ema_crossover":
                d = TS.ema_crossover(d, self.current_index, self.indicators["ema_short"]["values"], self.indicators["ema_long"]["values"])
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            log.error(f"make_decision() - strategy: {self.strategy}, Info: {(exc_obj, fname, exc_tb.tb_lineno)}, Error: {e}")
        try:
            if d != -99 and self.TP_SL_choice not in custom_tp_sl_functions:
                self.update_TP_SL()
                sl, tp = TS.SetSLTP(self.stop_loss_val, self.take_profit_val, self.peaks, self.troughs, self.Close,
                                    self.High, self.Low, d, self.SL_mult, self.TP_mult, self.TP_SL_choice, self.current_index)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            log.error(f"make_decision() - SetSLTP choice: {self.TP_SL_choice}, Info: {(exc_obj, fname, exc_tb.tb_lineno)}, Error: {e}")
        return d, sl, tp

    def check_close_pos(self, trade_direction):
        close_pos = 0
        try:
            if self.strategy == 'heikin_ashi_ema2':
                _, close_pos = TS.heikin_ashi_ema2(self.Open_H, self.High_H, self.Low_H, self.Close_H, -99, trade_direction, 0,
                                                   self.indicators["fastd"]["values"], self.indicators["fastk"]["values"],
                                                   self.indicators["EMA"]["values"], self.current_index)
            elif self.strategy == 'heikin_ashi_ema':
                _, close_pos = TS.heikin_ashi_ema(self.Open_H, self.Close_H, -99, trade_direction, 0,
                                                  self.indicators["fastd"]["values"], self.indicators["fastk"]["values"],
                                                  self.indicators["EMA"]["values"], self.current_index)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            log.error(f"check_close_pos() - strategy: {self.strategy}, Info: {(exc_obj, fname, exc_tb.tb_lineno)}, Error: {e}")
        return close_pos

    def _pop_all(self, idx):
        for a in ("Date","Close","Volume","High","Low","Open","Open_H","Close_H","High_H","Low_H"):
            getattr(self, a).pop(idx)

    def remove_last_candle(self):  self._pop_all(-1)
    def remove_first_candle(self): self._pop_all(0)

    def consume_new_candle(self, k):
        self.Date.append(int(k['T']))
        self.Close.append(float(k['c']))
        self.Volume.append(float(k['q']))
        self.High.append(float(k['h']))
        self.Low.append(float(k['l']))
        self.Open.append(float(k['o']))

    def generate_new_heikin_ashi(self):
        self.Open_H.append((self.Open_H[-1] + self.Close_H[-1]) / 2)
        self.Close_H.append((self.Open[-1] + self.Close[-1] + self.Low[-1] + self.High[-1]) / 4)
        self.High_H.append(max(self.High[-1], self.Open_H[-1], self.Close_H[-1]))
        self.Low_H.append(min(self.Low[-1], self.Open_H[-1], self.Close_H[-1]))
