import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

import asyncio, os, multiprocessing
from queue import Queue
from threading import Thread
from LiveTradingConfig import *
import SharedHelper
from Helper import *
from TradeManager import *

if __name__ == '__main__':
    try:
        log.info('='*60)
        log.info('BINANCE FUTURES TRADING BOT')
        log.info('='*60)
        log.info(f'Strategy: {trading_strategy}')
        log.info(f'Interval: {interval} | Leverage: {leverage}x | Order Size: {order_size}%')
        log.info('-'*60)
        log.info(f'TP/SL: {TP_SL_choice} | SL: {SL_mult}x | TP: {TP_mult}x')
        log.info(f'Trailing Stop: {use_trailing_stop} | Callback: {trailing_stop_callback}')
        log.info(f'Trading Threshold: {trading_threshold}% | Market Orders: {use_market_orders}')
        log.info('-'*60)
        symbols_display = ', '.join(symbols_to_trade) if not trade_all_symbols else 'ALL SYMBOLS'
        log.info(f'Symbols: {symbols_display}')
        log.info(f'Max Positions: {max_number_of_positions} | Multiprocessing: {use_multiprocessing_for_trade_execution}')
        log.info('='*60)
        if os.name == 'nt': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        Q = multiprocessing.Queue if use_multiprocessing_for_trade_execution else Queue
        signal_queue, print_trades_q = Q(), Q()
        
        log.info('Connecting to Binance API...')
        python_binance_client = Client(api_key=API_KEY, api_secret=API_SECRET)
        client = CustomClient(python_binance_client)
        
        if trade_all_symbols: symbols_to_trade = SharedHelper.get_all_symbols(python_binance_client, coin_exclusion_list)
        client.set_leverage(symbols_to_trade)
        Bots = []
        client.setup_bots(Bots, symbols_to_trade, signal_queue, print_trades_q)
        client.start_websockets(Bots)
        
        if use_multiprocessing_for_trade_execution:
            new_trade_loop = multiprocessing.Process(target=start_new_trades_loop_multiprocess, args=(python_binance_client, signal_queue, print_trades_q))
            new_trade_loop.start()
        else:
            TM = TradeManager(python_binance_client, signal_queue, print_trades_q)
            new_trade_loop = Thread(target=TM.new_trades_loop, daemon=True)
            new_trade_loop.start()
        
        Thread(target=client.ping_server_reconnect_sockets, args=(Bots,), daemon=True).start()
        if auto_calculate_buffer:
            buffer = convert_buffer_to_string(SharedHelper.get_required_buffer(trading_strategy))
        Thread(target=client.combine_data, args=(Bots, symbols_to_trade, buffer), daemon=True).start()
        
        log.info('Trading bot started successfully')
        new_trade_loop.join()
        
    except KeyboardInterrupt:
        log.info('Bot stopped by user')
    except Exception as e:
        if 'APIError' in str(type(e).__name__) or 'BinanceAPIException' in str(type(e).__name__):
            log.error('Failed to connect to Binance API')
            log.error('Please check: API keys, network connection, or Binance service status')
        elif 'Invalid API-key' in str(e):
            log.error('Invalid API credentials. Please check API_KEY and API_SECRET in LiveTradingConfig.py')
        else:
            log.error(f'Unexpected error: {e}')
        import sys
        sys.exit(1)
