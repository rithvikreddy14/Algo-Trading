# trading_strategy/indicators.py

import pandas as pd
import pandas_ta as ta # Import the pandas_ta library
import logging

logger = logging.getLogger(__name__)

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds RSI (14-period), 20-Day Simple Moving Average (SMA),
    and 50-Day Simple Moving Average (SMA) to the DataFrame.

    Args:
        df (pd.DataFrame): DataFrame with 'close' prices and 'volume'.

    Returns:
        pd.DataFrame: The original DataFrame with new columns for indicators.
                      Returns an empty DataFrame if input is invalid.
    """
    if not isinstance(df, pd.DataFrame) or df.empty:
        logger.error("Input DataFrame is invalid or empty for indicator calculation.")
        return pd.DataFrame()

    if 'close' not in df.columns:
        logger.error("DataFrame must contain a 'close' column for indicator calculation.")
        return pd.DataFrame()

    df_copy = df.copy() # Work on a copy to avoid modifying the original DataFrame directly

    try:
        # Calculate RSI (default period is 14)
        # The result column will be named 'RSI_14' by default by pandas_ta
        df_copy.ta.rsi(append=True)
        
        # Calculate 20-Day Simple Moving Average
        # The result column will be named 'SMA_20' by default
        df_copy.ta.sma(length=20, append=True)
        
        # Calculate 50-Day Simple Moving Average
        # The result column will be named 'SMA_50' by default
        df_copy.ta.sma(length=50, append=True)
        
        # Rename columns for easier access and consistency
        df_copy.rename(columns={
            'RSI_14': 'rsi',
            'SMA_20': '20_dma',
            'SMA_50': '50_dma'
        }, inplace=True)
        
        logger.info("RSI, 20-DMA, and 50-DMA indicators added successfully.")
        return df_copy
    
    except Exception as e:
        logger.error(f"Error adding indicators: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    # This block runs only when indicators.py is executed directly
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    print("\n--- Testing Indicators Module ---")
    # Create a dummy DataFrame for testing
    data = {
        'open': [100, 102, 101, 105, 103, 107, 106, 110, 109, 112, 111, 115, 114, 118, 117, 120, 119, 122, 121, 125, 124, 128, 127, 130, 129, 133, 132, 135, 134, 138, 137, 140, 139, 142, 141, 145, 144, 148, 147, 150, 149, 152, 151, 155, 154, 158, 157, 160, 159, 162],
        'high': [103, 104, 105, 107, 106, 109, 108, 112, 111, 114, 113, 117, 116, 120, 119, 122, 121, 124, 123, 127, 126, 130, 129, 132, 131, 135, 134, 137, 136, 140, 139, 142, 141, 144, 143, 147, 146, 150, 149, 152, 151, 154, 153, 157, 156, 160, 159, 162, 161, 164],
        'low': [99, 101, 100, 103, 102, 105, 104, 108, 107, 110, 109, 113, 112, 116, 115, 118, 117, 120, 119, 122, 121, 125, 124, 127, 126, 130, 129, 132, 131, 134, 133, 136, 135, 138, 137, 141, 140, 143, 142, 145, 144, 147, 146, 149, 148, 152, 151, 154, 153, 156],
        'close': [101, 103, 102, 104, 105, 108, 107, 109, 110, 113, 112, 114, 115, 117, 118, 121, 120, 123, 122, 124, 125, 127, 128, 129, 130, 132, 133, 134, 135, 137, 138, 139, 140, 141, 142, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158],
        'volume': [100000, 120000, 110000, 130000, 125000, 140000, 135000, 150000, 145000, 160000, 155000, 170000, 165000, 180000, 175000, 190000, 185000, 200000, 195000, 210000, 205000, 220000, 215000, 230000, 225000, 240000, 235000, 250000, 245000, 260000, 255000, 270000, 265000, 280000, 275000, 290000, 285000, 300000, 295000, 310000, 305000, 320000, 315000, 330000, 325000, 340000, 335000, 350000, 345000, 360000]
    }
    # Create enough data points for 50-SMA and RSI (at least 50 for 50-SMA, 14 for RSI)
    # Let's create 100 data points for better testing
    dates = pd.date_range(start='2024-01-01', periods=len(data['close']), freq='D')
    dummy_df = pd.DataFrame(data, index=dates)

    df_with_indicators = add_indicators(dummy_df)
    
    if not df_with_indicators.empty:
        print("\nDataFrame with indicators (last 10 rows):")
        print(df_with_indicators[['close', 'rsi', '20_dma', '50_dma']].tail(10))
        # Check for NaNs at the beginning due to indicator calculation
        print(f"\nNumber of NaN rows after indicator calculation: {df_with_indicators.isnull().any(axis=1).sum()}")
    else:
        print("Indicator calculation failed.")