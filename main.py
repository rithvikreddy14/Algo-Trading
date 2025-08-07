# main.py

import logging
import config
from trading_strategy.data_fetcher import get_all_stock_data
from trading_strategy.backtester import Backtester
from sheets_automation.sheets_logger import update_sheets

# Import for bonus tasks
from ml_model.predictor import train_and_predict
from telegram_alerts.alerter import send_alert

# Configure basic logging for the entire application
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.StreamHandler() # Output logs to console
                        # Optional: Add FileHandler for logging to a file
                        # logging.FileHandler("algo_trading.log")
                    ])

logger = logging.getLogger(__name__)

def run_algo_trading_system():
    """
    Main function to execute the algo trading system workflow:
    1. Fetches stock data.
    2. Runs the trading strategy backtest for each stock.
    3. Logs the results to Google Sheets.
    4. Runs ML model and sends Telegram alerts (Bonus Tasks).
    """
    logger.info("--- Starting Algo Trading System ---")
    
    # --- 1. Data Ingestion ---
    logger.info("Step 1: Fetching stock data...")
    # Pass API key and stock symbols directly from config
    stock_data = get_all_stock_data(config.ALPHA_VANTAGE_API_KEY, config.STOCK_SYMBOLS)
    
    if not stock_data:
        logger.error("Failed to fetch any stock data. Aborting system run.")
        send_alert("Algo Trading System: Failed to fetch stock data. Check API key and internet.", config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHAT_ID) # Corrected
        return
    logger.info(f"Successfully fetched data for {len(stock_data)} stock(s).")
    
    # --- 2. Run Trading Strategy & Backtest ---
    logger.info("Step 2: Running trading strategy backtests...")
    all_backtest_results = []
    for symbol, df in stock_data.items():
        if df.empty:
            logger.warning(f"Skipping backtest for {symbol} as its DataFrame is empty.")
            continue
        
        backtester = Backtester(symbol, df)
        backtester.run_strategy()
        results = backtester.get_results()
        all_backtest_results.append(results)
        logger.info(f"Backtest completed for {symbol}. Total P&L: {results['pnl']:.2f}")
        
        # Example of sending a Telegram alert for a significant trade or outcome
        if results['total_trades'] > 0:
            alert_msg = (f"Algo Trading System: Backtest for {symbol} completed.\n"
                         f"Total P&L: {results['pnl']:.2f}\n"
                         f"Win Ratio: {results['win_ratio']:.2f}%\n"
                         f"Total Trades: {results['total_trades']}")
            send_alert(alert_msg, config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHAT_ID) # Corrected

    if not all_backtest_results:
        logger.warning("No backtest results generated for any stock. Skipping Google Sheets update.")
        send_alert("Algo Trading System: No backtest results generated.", config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHAT_ID) # Corrected
        return

    # --- 3. Google Sheets Automation ---
    logger.info("Step 3: Updating Google Sheets with results...")
    try:
        # Pass Google Sheets config directly
        update_sheets(all_backtest_results, config.GOOGLE_SHEET_KEY_PATH, config.GOOGLE_SHEET_TITLE)
        logger.info("Google Sheets updated successfully.")
        send_alert("Algo Trading System: Google Sheets updated successfully with backtest results.", config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHAT_ID) # Corrected
    except Exception as e:
        logger.error(f"Error updating Google Sheets: {e}")
        send_alert(f"Algo Trading System: Error updating Google Sheets: {e}", config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHAT_ID) # Corrected

    # --- 4. ML Automation (Bonus) ---
    logger.info("Step 4 (Bonus): Running ML model for prediction...")
    for symbol, df in stock_data.items():
        if not df.empty and 'close' in df.columns and 'volume' in df.columns:
            try:
                logger.info(f"Training ML model for {symbol}...")
                model, accuracy = train_and_predict(df)
                if model is not None and accuracy is not None:
                    logger.info(f"ML model for {symbol} trained with accuracy: {accuracy:.2f}")
                    send_alert(f"ML model for {symbol} trained. Accuracy: {accuracy:.2f}", config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHAT_ID) # Corrected
                else:
                    logger.warning(f"ML model training skipped or failed for {symbol}.")
                    send_alert(f"ML model training skipped or failed for {symbol}.", config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHAT_ID) # Corrected
            except Exception as e:
                logger.error(f"Error running ML model for {symbol}: {e}")
                send_alert(f"Algo Trading System: Error running ML model for {symbol}: {e}", config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHAT_ID) # Corrected
        else:
            logger.warning(f"Skipping ML model for {symbol} due to insufficient data (missing 'close' or 'volume').")

    logger.info("--- Algo Trading System Finished ---")
    send_alert("Algo Trading System: All processes completed.", config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHAT_ID) # Corrected

if __name__ == "__main__":
    # This block ensures the main function is called when the script is executed
    run_algo_trading_system()