# Binance Futures Trading Bot - Installation Guide

Technical-analysis–driven crypto trading bot for **Binance Futures**.

## System Requirements

- **Operating System**: Windows 7/8/10/11
- **Python**: 3.7 or higher
- **Internet Connection**: Required for API communication
- **Time Sync**: Critical for live trading on Windows

### Windows Time Synchronization

Configure Windows to sync time daily, or Binance may reject orders due to timestamp drift.

1. Go to **Start** and type "Task Scheduler"
2. Create a new task to sync time periodically
3. Set to run `w32tm /resync` daily

## Installation

### Step 1: Clone Repository

Windows and Linux users should use this guide, but macOS users can utilize the available [DMG file](../../releases).





Installation Check: Git & Python on Windows.



Install Git for Windows via: https://git-scm.com/install/windows  



Install Python for Windows via: https://www.python.org/ftp/python/3.13.12/python-3.13.12-amd64.exe  



Open a GIT CMD window.






```bash
git clone https://github.com/thomasdutraa07/Trading-Bot-for-Binance-Future.git
cd Trading-Bot-for-Binance-Future
```

### Step 2: Install Dependencies

```bash
py -m pip install -r requirements.txt
```

This will install all required packages:
- `python-binance` - Binance API wrapper
- `colorlog` - Colored logging output
- `pandas` - Data analysis
- `ta` - Technical analysis library
- Other dependencies

### Step 3: Configure Binance API

1. Create a Binance account at https://binance.com
2. Go to **API Management** in account settings
3. Click **Create API**
4. Enable the following permissions:
   - Read
   - Trade
   - Futures
   - Withdrawals (optional)
5. Save your `API Key` and `Secret Key`

### Step 4: Configure Bot Settings

Edit `LiveTradingConfig.py` with your settings:

```python
# Binance API credentials
api_key = 'your_api_key_here'
api_secret = 'your_secret_key_here'

# Trading parameters
leverage = 10
order_size = 20  # in USDT
max_number_of_positions = 1

# Strategy selection
trading_strategy = 'tripleEMAStochasticRSIATR'

# Symbols to trade
trade_all_symbols = False
symbols_to_trade = ['BTCUSDT', 'ETHUSDT']
```

### Step 5: Run the Bot

```bash
py LiveTrading.py
```

The bot will start monitoring the market and executing trades based on your configured strategy.

## Configuration Guide

### Trading Parameters

**max_number_of_positions**
- Set to `1` for single-position trading
- Increase to trade multiple symbols simultaneously

**leverage**
- Adjust leverage multiplier (e.g., 5, 10, 20)
- Higher leverage = higher risk

**order_size**
- Position size in USDT
- Start small while testing strategies

**symbols_to_trade**
- List of trading pairs: `['BTCUSDT', 'ETHUSDT', 'BNBUSDT']`
- Set `trade_all_symbols = True` to trade all available symbols

### Trailing Stop Configuration

Enable trailing stop to lock in profits:

```python
use_trailing_stop = True
trailing_stop_callback = 0.5  # 0.5% callback
```

- Minimum value: `0.001` (0.1%)
- Maximum value: `5` (5%)
- Trailing stop activates when take-profit margin is reached

### Take Profit / Stop Loss Modes

**TP_SL_choice** options:
- `'USDT'` - Fixed USDT amount
- `'%'` - Percentage of position
- `'x (ATR)'` - Multiple of Average True Range
- `'x (Swing High/Low) level 1/2/3'` - Based on swing points
- `'x (Swing Close) level 1/2/3'` - Based on close prices

**Multipliers:**
- `SL_mult` - Stop loss multiplier
- `TP_mult` - Take profit multiplier

Example:
```python
TP_SL_choice = 'USDT'
SL_mult = 1  # Stop loss at -$1
TP_mult = 2  # Take profit at +$2
```

### Available Strategies (11)

1. `StochRSIMACD`
2. `tripleEMAStochasticRSIATR`
3. `tripleEMA`
4. `breakout`
5. `stochBB`
6. `goldenCross`
7. `candle_wick`
8. `fibMACD`
9. `EMA_cross`
10. `heikin_ashi_ema2`
11. `heikin_ashi_ema`

Select strategy in `LiveTradingConfig.py`:
```python
trading_strategy = 'tripleEMAStochasticRSIATR'
```

### Timeframe Selection

**interval** - Trading timeframe:
- `1m, 3m, 5m, 15m, 30m` - Short-term
- `1h, 2h, 4h` - Medium-term
- `6h, 8h, 12h, 1d` - Long-term

## Creating Custom Strategies

### Step 1: Implement Strategy

Add your strategy function to `TradingStrats.py`:

```python
def my_custom_strategy(df, current_price):
    # Your strategy logic here
    
    # Calculate entry signals
    if buy_condition:
        direction = 'LONG'
    elif sell_condition:
        direction = 'SHORT'
    else:
        direction = None
    
    # Calculate SL and TP
    stop_loss = current_price * 0.98
    take_profit = current_price * 1.02
    
    return direction, stop_loss, take_profit
```

### Step 2: Register Strategy

Reference your strategy in `Bot_Class.Bot.make_decision()`.

### Required Return Values

Your strategy **must return**:
- `Trade_Direction` - 'LONG', 'SHORT', or None
- `stop_loss_val` - Stop loss price
- `take_profit_val` - Take profit price

## Troubleshooting

**"Timestamp for this request was 1000ms ahead"**
- Sync Windows time as described above
- Check system clock accuracy

**"API key does not have permission"**
- Enable Futures permission in API settings
- Recreate API key with correct permissions

**Bot not opening positions**
- Verify sufficient balance in Futures wallet
- Check strategy signals are generating
- Review logs in console output

**Orders rejected**
- Check minimum order size for symbol
- Verify leverage settings are allowed
- Ensure balance covers margin requirements

## Risk Warning

⚠️ **Use at your own risk**

- Futures trading is highly leveraged and risky
- Always use stop losses
- Start with small position sizes
- Test strategies thoroughly before live trading
- Never invest more than you can afford to lose

## Support

- Repository: https://github.com/thomasdutraa07/Trading-Bot-for-Binance-Future
- Issues: https://github.com/thomasdutraa07/Trading-Bot-for-Binance-Future/issues

If you find this useful, please star the repository!