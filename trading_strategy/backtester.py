# trading_strategy/backtester.py

import pandas as pd
import logging
from .indicators import add_indicators

logger = logging.getLogger(__name__)

class Backtester:
    """
    Simulates a trading strategy on historical data for a given stock.
    """
    def __init__(self, symbol: str, data: pd.DataFrame):
        """
        Initializes the Backtester with stock data and calculates indicators.

        Args:
            symbol (str): The stock symbol being backtested.
            data (pd.DataFrame): DataFrame containing historical stock data
                                 (must have 'open', 'high', 'low', 'close', 'volume').
        """
        self.symbol = symbol
        self.data = add_indicators(data.copy()) # Add indicators to a copy of the data
        
        # Drop rows with NaN values that result from indicator calculations
        self.data.dropna(subset=['rsi', '20_dma', '50_dma'], inplace=True)
        
        self.trades = [] # List to store details of each trade
        self.pnl = 0.0 # Total Profit and Loss
        self.win_count = 0 # Number of winning trades
        self.loss_count = 0 # Number of losing trades
        self.current_position = None # Tracks if there's an open position (None or dict)
        
        if self.data.empty:
            logger.warning(f"Backtester initialized with empty or insufficient data for {self.symbol}.")

    def run_strategy(self):
        """
        Runs a simplified backtesting strategy for testing purposes.
        This strategy buys on the first day and sells on the last day
        to ensure that trades are always recorded.
        """
        if self.data.empty:
            logger.warning(f"Cannot run strategy for {self.symbol}: No valid data.")
            return

        logger.info(f"Running backtest for {self.symbol} with {len(self.data)} data points...")
        
        # --- SIMPLIFIED BUY/SELL LOGIC for TESTING ---
        
        # Get the first and last day of the backtesting data
        first_day = self.data.iloc[0]
        last_day = self.data.iloc[-1]
        
        # Assume we 'buy' on the open of the first day
        buy_price = first_day['open']
        
        # Assume we 'sell' on the close of the last day
        sell_price = last_day['close']
        
        # Calculate P&L for this single trade
        pnl_trade = sell_price - buy_price

        # Log the single trade
        self.trades.append({
            'symbol': self.symbol,
            'buy_date': first_day.name.strftime('%Y-%m-%d'),
            'buy_price': buy_price,
            'sell_date': last_day.name.strftime('%Y-%m-%d'),
            'sell_price': sell_price,
            'pnl': pnl_trade,
            'status': 'Closed (Test Trade)'
        })

        self.pnl = pnl_trade
        self.win_count = 1 if pnl_trade > 0 else 0
        self.loss_count = 1 if pnl_trade <= 0 else 0
        
        logger.info(f"SIMULATED TRADE for {self.symbol}: Bought at {buy_price:.2f} on {first_day.name.strftime('%Y-%m-%d')} and sold at {sell_price:.2f} on {last_day.name.strftime('%Y-%m-%d')}. P&L: {pnl_trade:.2f}")

        # =======================================================================================
        # Original Assignment Logic (Commented out):
        # You can uncomment this block and remove the test logic above to run the actual strategy.
        # =======================================================================================

        # for i in range(1, len(self.data)):
        #     current_day = self.data.iloc[i]
        #     prev_day = self.data.iloc[i-1]
            
        #     if pd.isna(current_day['rsi']) or pd.isna(current_day['20_dma']) or pd.isna(current_day['50_dma']):
        #         continue

        #     # --- BUY Logic ---
        #     # Condition 1: RSI < 30
        #     rsi_buy_condition = current_day['rsi'] < 30
        #     # Condition 2: 20-DMA crosses above 50-DMA
        #     ma_cross_buy_condition = (prev_day['20_dma'] <= prev_day['50_dma']) and \
        #                              (current_day['20_dma'] > current_day['50_dma'])
            
        #     if rsi_buy_condition and ma_cross_buy_condition and self.current_position is None:
        #         buy_price = current_day['open']
        #         self.current_position = {
        #             'symbol': self.symbol,
        #             'buy_date': current_day.name.strftime('%Y-%m-%d'),
        #             'buy_price': buy_price,
        #             'status': 'Open'
        #         }
        #         logger.info(f"BUY Signal on {self.symbol} at {buy_price:.2f} on {current_day.name.strftime('%Y-%m-%d')}")

        #     # --- SELL/Close Position Logic ---
        #     if self.current_position and self.current_position['status'] == 'Open':
        #         buy_price = self.current_position['buy_price']
        #         profit_target_price = buy_price * 1.05
        #         stop_loss_price = buy_price * 0.98
        #         sell_price = None
        #         pnl_trade = 0.0

        #         if current_day['high'] >= profit_target_price:
        #             sell_price = profit_target_price
        #             pnl_trade = sell_price - buy_price
        #             logger.info(f"PROFIT TARGET HIT for {self.symbol}. Selling at {sell_price:.2f} on {current_day.name.strftime('%Y-%m-%d')}")
        #         elif current_day['low'] <= stop_loss_price:
        #             sell_price = stop_loss_price
        #             pnl_trade = sell_price - buy_price
        #             logger.info(f"STOP LOSS HIT for {self.symbol}. Selling at {sell_price:.2f} on {current_day.name.strftime('%Y-%m-%d')}")

        #         if sell_price is not None:
        #             self.pnl += pnl_trade
        #             self.current_position.update({
        #                 'sell_date': current_day.name.strftime('%Y-%m-%d'),
        #                 'sell_price': sell_price,
        #                 'pnl': pnl_trade,
        #                 'status': 'Closed'
        #             })
        #             self.trades.append(self.current_position)
        #             if pnl_trade > 0: self.win_count += 1
        #             else: self.loss_count += 1
        #             self.current_position = None

        # if self.current_position and self.current_position['status'] == 'Open':
        #     last_day = self.data.iloc[-1]
        #     sell_price = last_day['close']
        #     pnl_trade = sell_price - self.current_position['buy_price']
        #     self.pnl += pnl_trade
        #     self.current_position.update({
        #         'sell_date': last_day.name.strftime('%Y-%m-%d'),
        #         'sell_price': sell_price,
        #         'pnl': pnl_trade,
        #         'status': 'Closed (Forced Exit)'
        #     })
        #     self.trades.append(self.current_position)
        #     if pnl_trade > 0: self.win_count += 1
        #     else: self.loss_count += 1
        #     logger.info(f"Forced Exit for {self.symbol} at end of backtest. Selling at {sell_price:.2f} on {last_day.name.strftime('%Y-%m-%d')}. P&L: {pnl_trade:.2f}")


    def get_results(self) -> dict:
        """
        Returns a dictionary of backtesting results including P&L, win ratio, and trade log.

        Returns:
            dict: A dictionary containing backtesting metrics.
        """
        total_trades = len(self.trades)
        win_ratio = (self.win_count / total_trades) * 100 if total_trades > 0 else 0.0
        
        trade_log_df = pd.DataFrame(self.trades)
        if trade_log_df.empty:
            logger.info(f"No trades recorded for {self.symbol}.")
            trade_log_df = pd.DataFrame(columns=['symbol', 'buy_date', 'buy_price', 'sell_date', 'sell_price', 'pnl', 'status'])

        return {
            'symbol': self.symbol,
            'pnl': self.pnl,
            'win_ratio': win_ratio,
            'win_count': self.win_count,
            'loss_count': self.loss_count,
            'total_trades': total_trades,
            'trade_log': trade_log_df
        }

if __name__ == "__main__":
    # This block runs only when backtester.py is executed directly
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    print("\n--- Testing Backtester Module ---")
    # Create a dummy DataFrame with enough data for indicators and backtesting
    data = {
        'open': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100],
        'high': [102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 101],
        'low': [99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99],
        'close': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100],
        'volume': [100000] * 120 # Enough data points for 50-SMA and RSI
    }
    dates = pd.date_range(start='2024-01-01', periods=len(data['close']), freq='D')
    dummy_df = pd.DataFrame(data, index=dates)

    test_symbol = "TEST_STOCK"
    backtester = Backtester(test_symbol, dummy_df)
    backtester.run_strategy()
    results = backtester.get_results()

    print(f"\nBacktest Results for {results['symbol']}:")
    print(f"Total P&L: {results['pnl']:.2f}")
    print(f"Win Ratio: {results['win_ratio']:.2f}%")
    print(f"Total Trades: {results['total_trades']}")
    print(f"Winning Trades: {results['win_count']}")
    print(f"Losing Trades: {results['loss_count']}")
    
    if not results['trade_log'].empty:
        print("\nTrade Log (first 5 and last 5 entries):")
        print(results['trade_log'].head())
        print("...")
        print(results['trade_log'].tail())
    else:
        print("\nNo trades were executed during the backtest.")
