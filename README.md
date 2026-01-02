# Binance Futures Trading Bot (Python)

Technical-analysis–driven crypto trading bot for **Binance Futures**.

## Status
- **OS**: Windows 7,8,10,11 only
- **Time sync (critical for live trading on Windows):** Configure Windows to sync time daily or Binance may reject orders due to timestamp drift. Example guide: https://www.makeuseof.com/tag/synchronise-computer-time-internet-custom-schedule-windows-7/#:~:text=Go%20to%20%3E%20Start%20and%20type,on%20the%20right%20hand%20side

## Features
- 11 prebuilt strategies
- Single or multi-symbol trading
- Trailing stop (configurable)
- Flexible TP/SL modes and multipliers

## Quick Start

### **Installation Walkthrough:** 
This guide is for Windows and macOS. macOS users can alternatively download and run the [DMG file](../../releases).


```bash
pip install -r requirements.txt
```

```bash
python LiveTrading.py
```

> **Risk notice:** Use strategies at your own risk. Futures are highly leveraged; always apply strict risk management and use stop losses.

## Binance Setup
1. Create a Binance account.
2. In **API Management**, create a new API key.
3. Enable permissions: **Read**, **Trade**, **Futures**, **Withdrawals**.
4. Put `api_key` and `api_secret` into **`liveTradingConfig.py`**.

## Configuration (`LiveTradingConfig.py`)
- **max_number_of_positions**: Set to `1` for single-position trading; increase to trade multiple symbols.
- **leverage**, **order_size**: Adjust to preference.
- **symbols_to_trade**: List of symbols. To trade all, set **trade_all_symbols = True**.
- **Trailing stop**: Set **use_trailing_stop = True**; tune **trailing_stop_callback** (min `0.001` = 0.1%, max `5` = 5%). The trailing stop is armed when the strategy’s take‑profit margin is reached.
- **Close conditions**: `check_close_pos()` must return a `close_pos` flag. (Currently **not functional**; requires update for new bot.)
- **Strategy**: Set **trading_strategy** to one of the built-ins or your custom function.
- **Built‑in strategies (11)**: `StochRSIMACD`, `tripleEMAStochasticRSIATR`, `tripleEMA`, `breakout`, `stochBB`, `goldenCross`, `candle_wick`, `fibMACD`, `EMA_cross`, `heikin_ashi_ema2`, `heikin_ashi_ema`.
- **TP/SL mode — `TP_SL_choice`**: One of  
  `USDT`, `%`, `x (ATR)`, `x (Swing High/Low) level 1/2/3`, `x (Swing Close) level 1/2/3`.
- **Multipliers**: **SL_mult**, **TP_mult** scale the chosen `TP_SL_choice`.  
  *Example:* `TP_SL_choice='USDT'`, `SL_mult=1`, `TP_mult=2` → SL = $1, TP = $2.
- **interval**: One of `1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d`.

## Custom Strategies
- Implement strategy functions in **`TradingStrats.py`**.
- Reference them in **`Bot_Class.Bot.make_decision()`**.
- Your **`make_decision()`** **must return**:  
  `Trade_Direction, stop_loss_val, take_profit_val`.

## Share
If you find this useful, please share the repository.