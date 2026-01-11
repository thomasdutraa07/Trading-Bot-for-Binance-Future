from LiveTradingConfig import *
from Logger import *

def USDT_SL_TP(options):
    """TP/SL when base unit is USDT and depends on filled position size."""
    q = round(1 / options['position_size'], 6)
    return SL_mult * q, TP_mult * q

def candle_wick(Trade_Direction, Close, Open, High, Low, current_index):
    """3 candles trend + opposite candle with long wick."""
    i = current_index
    if Close[i-4] < Close[i-3] < Close[i-2] and Close[i-1] < Open[i-1] and (High[i-1]-Open[i-1] + Close[i-1]-Low[i-1]) > 10*(Open[i-1]-Close[i-1]) and Close[i] < Close[i-1]:
        return 0
    if Close[i-4] > Close[i-3] > Close[i-2] and Close[i-1] > Open[i-1] and (High[i-1]-Close[i-1] + Open[i-1]-Low[i-1]) > 10*(Close[i-1]-Open[i-1]) and Close[i] > Close[i-1]:
        return 1
    return Trade_Direction

def fibMACD(Trade_Direction, Close, Open, High, Low, MACD_signal, MACD, EMA200, current_index):
    """Trend pullback to Fibonacci levels + MACD cross + engulfing."""
    period = 100
    peaks, p_locs, troughs, t_locs = [], [], [], []
    for i in range(current_index - period, current_index - 2):
        if High[i] > max(High[i-1], High[i+1], High[i-2], High[i+2]):
            peaks.append(High[i]); p_locs.append(i)
        elif Low[i] < min(Low[i-1], Low[i+1], Low[i-2], Low[i+2]):
            troughs.append(Low[i]); t_locs.append(i)

    trend = 1 if Close[current_index] > EMA200[current_index] else 0 if Close[current_index] < EMA200[current_index] else -99
    max_pos = min_pos = -99

    if trend == 1:
        max_close, min_close = -1e9, 1e9
        max_flag = min_flag = 0
        for i in range(len(peaks)-1, -1, -1):
            if peaks[i] > max_close and max_flag < 2:
                max_close = peaks[i]; max_pos = p_locs[i]; max_flag = 0
            elif max_flag == 2: break
            else: max_flag += 1
        start = -99
        for i, loc in enumerate(t_locs):
            if loc < max_pos: start = i
            else: break
        for i in range(start, -1, -1):
            if troughs[i] < min_close and min_flag < 2:
                min_close = troughs[i]; min_pos = t_locs[i]; min_flag = 0
            elif min_flag == 2: break
            else: min_flag += 1

        f0 = max_close
        f1 = max_close - .236*(max_close-min_close)
        f2 = max_close - .382*(max_close-min_close)
        f3 = max_close - .5*(max_close-min_close)
        f4 = max_close - .618*(max_close-min_close)
        f5 = max_close - .786*(max_close-min_close)
        f6 = min_close

        i = current_index
        cond_macd = (MACD_signal[i-1] < MACD[i-1] or MACD_signal[i-2] < MACD[i-2]) and MACD_signal[i] > MACD[i]
        engulf_bull = Close[i-2] < Open[i-2] < Close[i-1] < Close[i]
        if (f0 > Low[i-2] > f1 and Close[i-3] > f1 and Close[i-4] > f1 and Close[-6] > f1 and engulf_bull and cond_macd) \
        or (f1 > Low[i-2] > f2 and Close[i-3] > f2 and Close[i-4] > f2 and Close[-6] > f2 and engulf_bull and cond_macd) \
        or (f2 > Low[i-1] > f3 and Close[i-2] > f3 and Close[i-3] > f3 and Close[i-4] > f3 and engulf_bull and cond_macd) \
        or (f3 > Low[i-1] > f4 and Close[i-2] > f4 and Close[i-3] > f4 and Close[i-4] > f4 and engulf_bull and cond_macd) \
        or (f4 > Low[i-1] > f5 and Close[i-2] > f5 and Close[i-3] > f5 and Close[i-4] > f5 and engulf_bull and cond_macd) \
        or (f5 > Low[i-1] > f6 and Close[i-2] > f6 and Close[i-3] > f6 and Close[i-4] > f6 and engulf_bull and cond_macd):
            return 1

    elif trend == 0:
        max_close, min_close = -1e9, 1e9
        max_flag = min_flag = 0
        for i in range(len(troughs)-1, -1, -1):
            if troughs[i] < min_close and min_flag < 2:
                min_close = troughs[i]; min_pos = t_locs[i]; min_flag = 0
            elif min_flag == 2: break
            else: min_flag += 1
        start = -99
        for i, loc in enumerate(p_locs):
            if loc < min_pos: start = i
            else: break
        for i in range(start, -1, -1):
            if peaks[i] > max_close and max_flag < 2:
                max_close = peaks[i]; max_pos = p_locs[i]; max_flag = 0
            elif max_flag == 2: break
            else: max_flag += 1

        f0 = min_close
        f1 = min_close + .236*(max_close-min_close)
        f2 = min_close + .382*(max_close-min_close)
        f3 = min_close + .5*(max_close-min_close)
        f4 = min_close + .618*(max_close-min_close)
        f5 = min_close + .786*(max_close-min_close)
        f6 = max_close

        i = current_index
        cond_macd = (MACD_signal[i-1] > MACD[i-1] or MACD_signal[i-2] > MACD[i-2]) and MACD_signal[i] < MACD[i]
        engulf_bear = Close[i-2] > Open[i-2] > Close[i-1] > Close[i]
        if (f0 < High[i-2] < f1 and Close[i-3] < f1 and Close[i-4] < f1 and Close[-6] < f1 and engulf_bear and cond_macd) \
        or (f1 < High[i-2] < f2 and Close[i-3] < f2 and Close[i-4] < f2 and Close[-6] < f2 and engulf_bear and cond_macd) \
        or (f2 < High[i-2] < f3 and Close[i-3] < f3 and Close[i-4] < f3 and Close[-6] < f3 and engulf_bear and cond_macd) \
        or (f3 < High[i-2] < f4 and Close[i-3] < f4 and Close[i-4] < f4 and Close[-6] < f4 and engulf_bear and cond_macd) \
        or (f4 < High[i-2] < f5 and Close[i-3] < f5 and Close[i-4] < f5 and Close[-6] < f5 and engulf_bear and cond_macd) \
        or (f5 < High[i-2] < f6 and Close[i-3] < f6 and Close[i-4] < f6 and Close[-6] < f6 and engulf_bear and cond_macd):
            return 0

    return Trade_Direction

def goldenCross(Trade_Direction, Close, EMA100, EMA50, EMA20, RSI, current_index):
    """EMA20/EMA50 cross with EMA100 and RSI direction filter."""
    i = current_index
    if Close[i] > EMA100[i] and RSI[i] > 50:
        if (EMA20[i-1] < EMA50[i-1] <= EMA20[i]) or (EMA20[i-2] < EMA50[i-2] <= EMA20[i]) or (EMA20[i-3] < EMA50[i-3] <= EMA20[i]):
            return 1
    elif Close[i] < EMA100[i] and RSI[i] < 50:
        if (EMA20[i-1] > EMA50[i-1] >= EMA20[i]) or (EMA20[i-2] > EMA50[i-2] >= EMA20[i]) or (EMA20[i-3] > EMA50[i-3] >= EMA20[i]):
            return 0
    return Trade_Direction

def StochRSIMACD(Trade_Direction, fastd, fastk, RSI, MACD, macdsignal, current_index):
    """StochRSI extremes + MACD cross + RSI direction."""
    i = current_index
    bull = (
        ((fastd[i] < 20 and fastk[i] < 20) and RSI[i] > 50 and MACD[i] > macdsignal[i] and MACD[i-1] < macdsignal[i-1]) or
        ((fastd[i-1] < 20 and fastk[i-1] < 20) and RSI[i] > 50 and MACD[i] > macdsignal[i] and MACD[i-2] < macdsignal[i-2] and fastd[i] < 80 and fastk[i] < 80) or
        ((fastd[i-2] < 20 and fastk[i-2] < 20) and RSI[i] > 50 and MACD[i] > macdsignal[i] and MACD[i-1] < macdsignal[i-1] and fastd[i] < 80 and fastk[i] < 80) or
        ((fastd[i-3] < 20 and fastk[i-3] < 20) and RSI[i] > 50 and MACD[i] > macdsignal[i] and MACD[i-2] < macdsignal[i-2] and fastd[i] < 80 and fastk[i] < 80)
    )
    bear = (
        ((fastd[i] > 80 and fastk[i] > 80) and RSI[i] < 50 and MACD[i] < macdsignal[i] and MACD[i-1] > macdsignal[i-1]) or
        ((fastd[i-1] > 80 and fastk[i-1] > 80) and RSI[i] < 50 and MACD[i] < macdsignal[i] and MACD[i-2] > macdsignal[i-2] and fastd[i] > 20 and fastk[i] > 20) or
        ((fastd[i-2] > 80 and fastk[i-2] > 80) and RSI[i] < 50 and MACD[i] < macdsignal[i] and MACD[i-1] > macdsignal[i-1] and fastd[i] > 20 and fastk[i] > 20) or
        ((fastd[i-3] > 80 and fastk[i-3] > 80) and RSI[i] < 50 and MACD[i] < macdsignal[i] and MACD[i-2] > macdsignal[i-2] and fastd[i] > 20 and fastk[i] > 20)
    )
    if bull: return 1
    if bear: return 0
    return Trade_Direction

def tripleEMA(Trade_Direction, EMA3, EMA6, EMA9, current_index):
    """Fast EMA crossing both M/L EMAs after sustained separation."""
    i = current_index
    if EMA3[i-4] > EMA6[i-4] > 0 and EMA3[i-4] > EMA9[i-4] and \
       EMA3[i-3] > EMA6[i-3] and EMA3[i-3] > EMA9[i-3] and \
       EMA3[i-2] > EMA6[i-2] and EMA3[i-2] > EMA9[i-2] and \
       EMA3[i-1] > EMA6[i-1] and EMA3[i-1] > EMA9[i-1] and \
       EMA3[i] < EMA6[i] and EMA3[i] < EMA9[i]:
        return 0
    if EMA3[i-4] < EMA6[i-4] and EMA3[i-4] < EMA9[i-4] and \
       EMA3[i-3] < EMA6[i-3] and EMA3[i-3] < EMA9[i-3] and \
       EMA3[i-2] < EMA6[i-2] and EMA3[i-2] < EMA9[i-2] and \
       EMA3[i-1] < EMA6[i-1] and EMA3[i-1] < EMA9[i-1] and \
       EMA3[i] > EMA6[i] and EMA3[i] > EMA9[i]:
        return 1
    return Trade_Direction

def heikin_ashi_ema2(Open_H, High_H, Low_H, Close_H, Trade_Direction, CurrentPos, Close_pos, fastd, fastk, EMA200, current_index):
    """Heikin Ashi + StochRSI crosses around EMA200 with pattern checks."""
    i = current_index
    if CurrentPos == -99:
        Trade_Direction = -99
        short_th, long_th = .7, .3
        if fastk[i-1] > fastd[i-1] and fastk[i] < fastd[i] and Close_H[i] < EMA200[i]:
            for k in range(10, 2, -1):
                if Close_H[-k] < Open_H[-k] and Open_H[-k] == High_H[-k]:
                    for j in range(k, 2, -1):
                        if Close_H[-j] > EMA200[-j] and Close_H[-j+1] < EMA200[-j+1] and Open_H[-j] > Close_H[-j]:
                            if all(fastd[-r] >= short_th and fastk[-r] >= short_th for r in range(j, 0, -1)):
                                return 0, Close_pos
        elif fastk[i-1] < fastd[i-1] and fastk[i] > fastd[i] and Close_H[i] > EMA200[i]:
            for k in range(10, 2, -1):
                if Close_H[-k] > Open_H[-k] and Open_H[-k] == Low_H[-k]:
                    for j in range(k, 2, -1):
                        if Close_H[-j] < EMA200[-j] and Close_H[-j+1] > EMA200[-j+1] and Open_H[-j] < Close_H[-j]:
                            if all(fastd[-r] <= long_th and fastk[-r] <= long_th for r in range(j, 0, -1)):
                                return 1, Close_pos
    elif CurrentPos == 1 and Close_H[i] < Open_H[i]:
        Close_pos = 1
    elif CurrentPos == 0 and Close_H[i] > Open_H[i]:
        Close_pos = 1
    else:
        Close_pos = 0
    return Trade_Direction, Close_pos

def heikin_ashi_ema(Open_H, Close_H, Trade_Direction, CurrentPos, Close_pos, fastd, fastk, EMA200, current_index):
    """Simpler HA + StochRSI + EMA200 filter."""
    i = current_index
    if CurrentPos == -99:
        Trade_Direction = -99
        short_th, long_th = .8, .2
        if fastk[i] > short_th and fastd[i] > short_th:
            for k in range(10, 2, -1):
                if fastd[-k] >= .8 and fastk[-k] >= .8:
                    for j in range(k, 2, -1):
                        if fastk[-j] > fastd[-j] and fastk[-j+1] < fastd[-j+1]:
                            if all(fastk[r] >= short_th and fastd[r] >= short_th for r in range(j, 2, -1)):
                                if Close_H[i-2] > EMA200[i-2] and Close_H[i-1] < EMA200[i-1] and Close_H[i] < Open_H[i]:
                                    return 0, Close_pos
        elif fastk[i] < long_th and fastd[i] < long_th:
            for k in range(10, 2, -1):
                if fastd[-k] <= .2 and fastk[-k] <= .2:
                    for j in range(k, 2, -1):
                        if fastk[-j] < fastd[-j] and fastk[-j+1] > fastd[-j+1] and fastk[i] < long_th and fastd[i] < long_th:
                            if all(fastk[r] <= long_th and fastd[r] <= long_th for r in range(j, 2, -1)):
                                if Close_H[i-2] < EMA200[i-2] and Close_H[i-1] > EMA200[i-1] and Close_H[i] > Open_H[i]:
                                    return 1, Close_pos
    elif CurrentPos == 1 and Close_H[i] < Open_H[i]:
        Close_pos = 1
    elif CurrentPos == 0 and Close_H[i] > Open_H[i]:
        Close_pos = 1
    else:
        Close_pos = 0
    return Trade_Direction, Close_pos

def tripleEMAStochasticRSIATR(Close, Trade_Direction, EMA50, EMA14, EMA8, fastd, fastk, current_index):
    """Trend filter by EMAs + StochRSI cross."""
    i = current_index
    if Close[i] > EMA8[i] > EMA14[i] > EMA50[i] and fastk[i] > fastd[i] and fastk[i-1] < fastd[i-1]:
        return 1
    if Close[i] < EMA8[i] < EMA14[i] < EMA50[i] and fastk[i] < fastd[i] and fastk[i-1] > fastd[i-1]:
        return 0
    return Trade_Direction

def stochBB(Trade_Direction, fastd, fastk, percent_B, current_index):
    """StochRSI extremes with Bollinger %B boundary check."""
    i = current_index
    b1, b2, b3 = percent_B[i], percent_B[i-1], percent_B[i-2]
    if fastk[i] < .2 and fastd[i] < .2 and fastk[i] > fastd[i] and fastk[i-1] < fastd[i-1] and (b1 < 0 or b2 < 0 or b3 < 0):
        return 1
    if fastk[i] > .8 and fastd[i] > .8 and fastk[i] < fastd[i] and fastk[i-1] > fastd[i-1] and (b1 > 1 or b2 > 1 or b3 > 1):
        return 0
    return Trade_Direction

def breakout(Trade_Direction, Close, VolumeStream, max_Close, min_Close, max_Vol, current_index):
    """Simple breakout with volume confirmation (invert=0 means trade breakout direction)."""
    i = current_index
    if Close[i] >= max_Close.iloc[i] and VolumeStream[i] >= max_Vol.iloc[i]:
        return 1
    if Close[i] <= min_Close.iloc[i] and VolumeStream[i] >= max_Vol.iloc[i]:
        return 0
    return Trade_Direction

def ema_crossover(Trade_Direction, current_index, ema_short, ema_long):
    """1-candle EMA cross."""
    i = current_index
    if ema_short[i-1] > ema_long[i-1] and ema_short[i] < ema_long[i]:
        return 0
    if ema_short[i-1] < ema_long[i-1] and ema_short[i] > ema_long[i]:
        return 1
    return Trade_Direction

def EMA_cross(Trade_Direction, EMA_short, EMA_long, current_index):
    """EMA_short flips after sustained separation from EMA_long."""
    i = current_index
    if EMA_short[i-4] > EMA_long[i-4] and EMA_short[i-3] > EMA_long[i-3] and EMA_short[i-2] > EMA_long[i-2] and EMA_short[i-1] > EMA_long[i-1] and EMA_short[i] < EMA_long[i]:
        return 0
    if EMA_short[i-4] < EMA_long[i-4] and EMA_short[i-3] < EMA_long[i-3] and EMA_short[i-2] < EMA_long[i-2] and EMA_short[i-1] < EMA_long[i-1] and EMA_short[i] > EMA_long[i]:
        return 1
    return Trade_Direction

def SetSLTP(stop_loss_val_arr, take_profit_val_arr, peaks, troughs, Close, High, Low, Trade_Direction, SL, TP, TP_SL_choice, current_index):
    """Compute absolute SL/TP from arrays or from swing points."""
    i = current_index
    tp = sl = -99
    if TP_SL_choice in ('%', 'x (ATR)'):
        tp = take_profit_val_arr[i]; sl = stop_loss_val_arr[i]
    elif TP_SL_choice.startswith('x (Swing High/Low) level'):
        high_swing, low_swing = High[i], Low[i]
        hf = lf = 0
        lvl = int(TP_SL_choice[-1])
        for j in range(i - lvl, -1, -1):
            if High[j] > high_swing and not hf and peaks[j]:
                high_swing = peaks[j]; hf = 1
            if Low[j] < low_swing and not lf and troughs[j]:
                low_swing = troughs[j]; lf = 1
            if (hf and Trade_Direction == 0) or (lf and Trade_Direction == 1): break
        if Trade_Direction == 0:
            sl = SL * (high_swing - Close[i]); tp = TP * sl
        elif Trade_Direction == 1:
            sl = SL * (Close[i] - low_swing); tp = TP * sl
    elif TP_SL_choice.startswith('x (Swing Close) level'):
        high_swing = low_swing = Close[i]
        hf = lf = 0
        lvl = int(TP_SL_choice[-1])
        for j in range(i - lvl, -1, -1):
            if Close[j] > high_swing and not hf and peaks[j]:
                high_swing = peaks[j]; hf = 1
            if Close[j] < low_swing and not lf and troughs[j]:
                low_swing = troughs[j]; lf = 1
            if (hf and Trade_Direction == 0) or (lf and Trade_Direction == 1): break
        if Trade_Direction == 0:
            sl = SL * (high_swing - Close[i]); tp = TP * sl
        elif Trade_Direction == 1:
            sl = SL * (Close[i] - low_swing); tp = TP * sl
    return sl, tp
