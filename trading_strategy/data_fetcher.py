# trading_strategy/data_fetcher.py

import pandas as pd
import requests
import time
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)

def fetch_daily_data(symbol: str, api_key: str) -> pd.DataFrame | None:
    """
    Fetches daily stock data for a given symbol from Alpha Vantage.

    Args:
        symbol (str): The stock symbol (e.g., "RELIANCE.BSE").
        api_key (str): Your Alpha Vantage API key.

    Returns:
        pd.DataFrame | None: A DataFrame containing daily stock data (open, high, low, close, volume)
                             with a DatetimeIndex, or None if an error occurs.
    """
    logger.info(f"Attempting to fetch data for {symbol}...")
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": "full",  # 'full' for historical data, 'compact' for recent 100 days
        "apikey": api_key
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        data = response.json()
        
        # Alpha Vantage often returns a "Note" if the API call limit is hit
        if "Note" in data:
            logger.warning(f"Alpha Vantage API call limit reached for {symbol}. Waiting for 60 seconds...")
            time.sleep(60) # Wait for 1 minute before retrying
            return fetch_daily_data(symbol, api_key) # Recursive call to retry
        
        # Check if the API returned an error message
        if "Error Message" in data:
            logger.error(f"Alpha Vantage API error for {symbol}: {data['Error Message']}")
            return None

        time_series = data.get("Time Series (Daily)", {})
        if not time_series:
            logger.warning(f"No time series data found for {symbol}.")
            return None

        # Convert dictionary to DataFrame
        df = pd.DataFrame.from_dict(time_series, orient='index', dtype=float)
        df.columns = ['open', 'high', 'low', 'close', 'volume']
        df.index = pd.to_datetime(df.index)
        df = df.sort_index(ascending=True) # Ensure chronological order

        logger.info(f"Successfully fetched {len(df)} data points for {symbol}.")
        return df
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Network or API request error for {symbol}: {e}")
        return None
    except ValueError as e: # Catches JSON decoding errors
        logger.error(f"Error decoding JSON response for {symbol}: {e}. Response: {response.text[:200]}...")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred while fetching data for {symbol}: {e}")
        return None

def get_all_stock_data(api_key: str, stock_symbols: list[str]) -> dict[str, pd.DataFrame]:
    """
    Fetches daily data for a list of stock symbols.
    Filters the data to the last 6 months for backtesting.

    Args:
        api_key (str): The Alpha Vantage API key.
        stock_symbols (list[str]): A list of stock symbols.

    Returns:
        dict[str, pd.DataFrame]: A dictionary where keys are stock symbols
                                 and values are DataFrames of their daily data.
    """
    all_data = {}
    for symbol in stock_symbols:
        df = fetch_daily_data(symbol, api_key)
        if df is not None and not df.empty:
            # Filter data for the last 6 months
            six_months_ago = date.today() - timedelta(days=180)
            # Use .loc for label-based indexing to filter dates
            df_filtered = df.loc[df.index >= pd.Timestamp(six_months_ago)]
            
            if df_filtered.empty:
                logger.warning(f"No data available for {symbol} in the last 6 months after filtering.")
            else:
                all_data[symbol] = df_filtered
                logger.info(f"Filtered {symbol} data to {len(df_filtered)} entries for the last 6 months.")
        else:
            logger.warning(f"Skipping {symbol} due to failed data fetch or empty DataFrame.")
    return all_data