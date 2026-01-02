import os, sys
import numpy as np
from Logger import *
import BotClass

def get_all_symbols(client, coin_exclusion_list):
    """Return tradable USDT symbols excluding those in the exclusion list."""
    return [s['symbol'] for s in client.futures_exchange_info()['symbols']
            if s['status'] == 'TRADING' and 'USDT' in s['symbol'] and '_' not in s['symbol'] and s['symbol'] not in coin_exclusion_list]

def compare_indicators(keys, ind_buf, ind_act):
    """Compare indicator sets to estimate required buffer size."""
    try:
        errs = []
        for k in keys:
            vb, va = ind_buf[k]['values'], ind_act[k]['values']
            if isinstance(vb, list):
                pairs = zip(va[-30:], vb[-30:])
                def sr(a, b): return (a - b) / a if a else 0
                errs.append(abs(sum(sr(a, b) for a, b in pairs)))
            else:
                a, b = va, vb
                errs.append(((a - b) / a) if a else 0)
        return sum(errs) / len(keys)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        log.warning(f"compare_indicators() - Info: {(exc_obj, fname, exc_tb.tb_lineno)}, Error: {e}")

def get_required_buffer(trading_strategy):
    """Calculate the minimal candle buffer ensuring indicator parity with live data."""
    log.info('get_required_buffer() - Calculating required buffer...')
    rng = np.random.default_rng(123)
    o = rng.uniform(2, 100, 20000)
    c = rng.uniform(2, 100, 20000)
    h = rng.uniform(2, 100, 20000)
    l = rng.uniform(2, 100, 20000)
    v = rng.uniform(2, 100_000_000, 20000)
    actual = BotClass.Bot('actual_values_bot', o, c, h, l, v, [], 3, 4, 0, 1, trading_strategy, '%', 1, 1, 1)
    for i in range(30, 20000):
        try:
            buf_bot = BotClass.Bot('buffer_bot', o[-i:], c[-i:], h[-i:], l[-i:], v[-i:], [], 3, 4, 0, 1, trading_strategy, '%', 1, 1, 1)
            err = compare_indicators(buf_bot.indicators.keys(), buf_bot.indicators, actual.indicators)
            log.debug(f'Error {err} with buffer {i} candles')
            if err < 1e-5: return i
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            log.warning(f"get_required_buffer() - Info: {(exc_obj, fname, exc_tb.tb_lineno)}, Error: {e}")
