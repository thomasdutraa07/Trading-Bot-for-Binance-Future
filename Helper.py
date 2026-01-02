import os, sys, time, math
from binance.client import Client
from binance import ThreadedWebsocketManager
import BotClass
from LiveTradingConfig import *
from Logger import *

def convert_buffer_to_string(buffer_int):
    """Convert candle count to Binance start_str like 'X hours/days ago'."""
    try:
        u = interval[-1]
        minutes = int(interval[:-1]) * (1 if u == 'm' else 60 if u == 'h' else 1440 if u == 'd' else 1)
        h = math.ceil((minutes * buffer_int) / 60)
        if h < 24:
            log.info(f'convert_buffer_to_string() - buffer: {h} hours ago')
            return f'{h} hours ago'
        d = math.ceil(h / 24)
        log.info(f'convert_buffer_to_string() - buffer: {d} days ago')
        return f'{d} days ago'
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        log.warning(f"convert_buffer_to_string() - Info: {(exc_obj, fname, exc_tb.tb_lineno)}, Error: {e}")

class CustomClient:
    def __init__(self, client: Client):
        self.client = client
        self.leverage = leverage
        self.twm = ThreadedWebsocketManager(api_key=API_KEY, api_secret=API_SECRET)
        self.number_of_bots = 0

    def set_leverage(self, symbols_to_trade: list[str]):
        """Set leverage per symbol as defined in config."""
        log.info("set_leverage() - Setting leverage...")
        i = 0
        while i < len(symbols_to_trade):
            sym = symbols_to_trade[i]
            log.info(f"set_leverage() - ({i+1}/{len(symbols_to_trade)}) {sym}")
            try:
                self.client.futures_change_leverage(symbol=sym, leverage=self.leverage)
                i += 1
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                log.warning(f"set_leverage() - Removing {sym}. Info: {(exc_obj, fname, exc_tb.tb_lineno)}, Error: {e}")
                symbols_to_trade.pop(i)

    def start_websockets(self, bots: list[BotClass.Bot]):
        """Start kline sockets for all bots."""
        self.twm.start()
        log.info("start_websockets() - Starting sockets...")
        i = 0
        while i < len(bots):
            b = bots[i]
            try:
                b.stream = self.twm.start_kline_futures_socket(callback=b.handle_socket_message, symbol=b.symbol, interval=interval)
                i += 1
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                log.warning(f"start_websockets() - {b.symbol}. Info: {(exc_obj, fname, exc_tb.tb_lineno)}, Error: {e}")
                bots.pop(i)
        self.number_of_bots = len(bots)

    def ping_server_reconnect_sockets(self, bots: list[BotClass.Bot]):
        """Keep connection alive and auto-reconnect failed sockets."""
        while True:
            time.sleep(15)
            self.client.futures_ping()
            for b in bots:
                if b.socket_failed:
                    try:
                        log.info(f"retry_websockets_job() - Resetting {b.symbol}")
                        self.twm.stop_socket(b.stream)
                        b.stream = self.twm.start_kline_futures_socket(b.handle_socket_message, symbol=b.symbol)
                        b.socket_failed = False
                        log.info("retry_websockets_job() - Reset OK")
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        log.error(f"retry_websockets_job() - {b.symbol}. Info: {(exc_obj, fname, exc_tb.tb_lineno)}, Error: {e}")

    def setup_bots(self, bots: list[BotClass.Bot], symbols_to_trade: list[str], signal_queue, print_trades_q):
        """Instantiate a Bot for each tradable symbol."""
        log.info("setup_bots() - Creating bots...")
        info = self.client.futures_exchange_info()['symbols']
        meta = {x['pair']: (int(x['pricePrecision']), int(x['quantityPrecision']), float(x['filters'][0]['tickSize'])) for x in info}

        i = 0
        while i < len(symbols_to_trade):
            sym = symbols_to_trade[i]
            if sym in meta:
                cp, op, tick = meta[sym]
                bots.append(BotClass.Bot(symbol=sym, Open=[], Close=[], High=[], Low=[], Volume=[], Date=[],
                                         OP=op, CP=cp, index=i, tick=tick, strategy=trading_strategy,
                                         TP_SL_choice=TP_SL_choice, SL_mult=SL_mult, TP_mult=TP_mult,
                                         signal_queue=signal_queue, print_trades_q=print_trades_q))
                i += 1
            else:
                log.info(f"setup_bots() - {sym} missing exchange info, removed")
                try:
                    symbols_to_trade.pop(i)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    log.warning(f"setup_bots() - Remove failed. Info: {(exc_obj, fname, exc_tb.tb_lineno)}, Error: {e}")
        log.info("setup_bots() - Done")

    def combine_data(self, bots: list[BotClass.Bot], symbols_to_trade: list[str], buffer):
        """Fetch historical data and merge with live stream so bots can trade immediately."""
        log.info("combine_data() - Merging historical + socket data...")
        i = 0
        while i < len(bots):
            b = bots[i]
            log.info(f"combine_data() - ({i+1}/{len(bots)}) {b.symbol}")
            dt, op, cl, hi, lo, vo = self.get_historical(b.symbol, buffer)
            try:
                for arr in (dt, op, cl, hi, lo, vo): arr.pop(-1)
                b.add_hist(Date_temp=dt, Open_temp=op, Close_temp=cl, High_temp=hi, Low_temp=lo, Volume_temp=vo)
                i += 1
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                try:
                    log.warning(f"combine_data() - Add failed. Info: {(exc_obj, fname, exc_tb.tb_lineno)}, Error: {e}")
                    self.twm.stop_socket(b.stream)
                    symbols_to_trade.pop(i); bots.pop(i); self.number_of_bots -= 1
                except Exception as e2:
                    exc_type2, exc_obj2, exc_tb2 = sys.exc_info()
                    fname2 = os.path.split(exc_tb2.tb_frame.f_code.co_filename)[1]
                    log.warning(f"combine_data() - Cleanup failed. Info: {(exc_obj2, fname2, exc_tb2.tb_lineno)}, Error: {e2}")
        log.info("combine_data() - All symbols ready. Scanning for trades...")

    def get_historical(self, symbol: str, buffer):
        """Download historical klines for a symbol."""
        O, H, L, C, V, D = [], [], [], [], [], []
        try:
            for k in self.client.futures_historical_klines(symbol, interval, start_str=buffer):
                D.append(int(k[6])); O.append(float(k[1])); C.append(float(k[4]))
                H.append(float(k[2])); L.append(float(k[3])); V.append(float(k[7]))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            log.error(f'get_historical() - {symbol}. Info: {(exc_obj, fname, exc_tb.tb_lineno)}, Error: {e}')
        return D, O, C, H, L, V

    def get_account_balance(self):
        """Return USDT futures wallet balance."""
        try:
            for x in self.client.futures_account_balance():
                if x['asset'] == 'USDT': return float(x['balance'])
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            log.error(f'get_account_balance() - Info: {(exc_obj, fname, exc_tb.tb_lineno)}, Error: {e}')

class Trade:
    def __init__(self, index: int, entry_price: float, position_size: float, take_profit_val: float,
                 stop_loss_val: float, trade_direction: int, order_id: int, symbol: str, CP: int, tick_size: float):
        self.index, self.symbol, self.entry_price, self.position_size = index, symbol, entry_price, position_size
        if trade_direction:
            self.TP_val, self.SL_val = entry_price + take_profit_val, entry_price - stop_loss_val
        else:
            self.TP_val, self.SL_val = entry_price - take_profit_val, entry_price + stop_loss_val
        self.CP, self.tick_size, self.trade_direction, self.order_id = CP, tick_size, trade_direction, order_id
        self.TP_id = self.SL_id = ''
        self.trade_status, self.trade_start = 0, ''
        self.Highest_val, self.Lowest_val = -9_999_999, 9_999_999
        self.trail_activated, self.same_candle = False, True
        self.current_price = 0
