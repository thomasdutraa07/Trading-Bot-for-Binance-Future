API_KEY = ''
API_SECRET = ''

trading_strategy = 'tripleEMAStochasticRSIATR' # Strategy (options: 'StochRSIMACD','tripleEMAStochasticRSIATR','tripleEMA','breakout','stochBB','goldenCross','candle_wick','fibMACD','EMA_cross','heikin_ashi_ema2','heikin_ashi_ema','ema_crossover')
TP_SL_choice = '%' 					# TP/SL base unit (options: 'USDT','%','x (ATR)','x (Swing High/Low) level 1','x (Swing High/Low) level 2','x (Swing High/Low) level 3','x (Swing Close) level 1','x (Swing Close) level 2','x (Swing Close) level 3')

leverage = 10
order_size = 3            			# % of account
interval = '1m'
SL_mult = 1.5             			# SL = SL_mult × TP_SL_choice
TP_mult = 1               			# TP = TP_mult × TP_SL_choice

trade_all_symbols = True
symbols_to_trade = ['BTCUSDT']
coin_exclusion_list = ['USDCUSDT', 'BTCDOMUSDT']  # Symbols to skip

use_trailing_stop = False
trailing_stop_callback = 0.1
trading_threshold = 0.3   			# Cancel if price moved this % from planned entry
use_market_orders = False
max_number_of_positions = 10
wait_for_candle_close = True        # If False, bot can enter before candle close
auto_calculate_buffer = True        # If False, set buffer manually
buffer = '3 hours ago'

LOG_LEVEL = 20                      # 50 CRITICAL | 40 ERROR | 30 WARNING | 20 INFO | 10 DEBUG
log_to_file = False                 # Also write logs to file

use_multiprocessing_for_trade_execution = True # Execution mode (set True if many symbols or reconnect issues; otherwise reduce symbols)
custom_tp_sl_functions = ['USDT'] 	# TP/SL functions requiring placed-trade context
make_decision_options = {} 			# Extra decision-making options