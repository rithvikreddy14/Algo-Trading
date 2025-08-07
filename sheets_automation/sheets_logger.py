# sheets_automation/sheets_logger.py

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def connect_to_sheets(key_path: str, sheet_title: str) -> gspread.Spreadsheet | None:
    """
    Connects to Google Sheets using a service account.

    Args:
        key_path (str): The path to the Google Service Account JSON key file.
        sheet_title (str): The title of the Google Spreadsheet to connect to.

    Returns:
        gspread.Spreadsheet | None: The Google Spreadsheet object if connection is successful,
                                    otherwise None.
    """
    try:
        # Define the scope for Google Sheets and Drive APIs
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        
        # Load credentials from the JSON key file
        creds = ServiceAccountCredentials.from_json_keyfile_name(key_path, scope)
        
        # Authorize the gspread client with the loaded credentials
        client = gspread.authorize(creds)
        
        # Open the spreadsheet by its title
        spreadsheet = client.open(sheet_title)
        logger.info(f"Successfully connected to Google Sheet: '{sheet_title}'")
        return spreadsheet
    except FileNotFoundError:
        logger.error(f"Credentials file not found at: {key_path}. Please ensure it exists.")
        return None
    except Exception as e:
        logger.error(f"Error connecting to Google Sheets: {e}. Check credentials and sheet permissions.")
        return None

def update_sheets(results_data: list[dict], key_path: str, sheet_title: str):
    """
    Updates the Google Sheet with trade logs, P&L summary, and win ratio.
    It creates the worksheets if they don't exist.

    Args:
        results_data (list[dict]): A list of dictionaries, where each dictionary
                                   contains backtesting results for a stock.
                                   Each dict should have 'symbol', 'pnl', 'win_ratio',
                                   'win_count', 'loss_count', 'total_trades', and 'trade_log' (DataFrame).
        key_path (str): The path to the Google Service Account JSON key file.
        sheet_title (str): The title of the Google Spreadsheet to update.
    """
    spreadsheet = connect_to_sheets(key_path, sheet_title)
    if spreadsheet is None:
        return # Exit if connection failed

    # Define worksheet names
    trade_log_ws_name = "Trade Log"
    pnl_summary_ws_name = "P&L Summary"
    win_ratio_ws_name = "Win Ratio"

    # Helper function to get or create a worksheet
    def get_or_create_worksheet(ws_name: str) -> gspread.Worksheet:
        try:
            worksheet = spreadsheet.worksheet(ws_name)
            worksheet.clear() # Clear existing content for fresh update
            logger.info(f"Cleared existing data in worksheet: '{ws_name}'")
            return worksheet
        except gspread.WorksheetNotFound:
            logger.info(f"Worksheet '{ws_name}' not found. Creating it...")
            worksheet = spreadsheet.add_worksheet(ws_name, rows=1, cols=1)
            logger.info(f"Created new worksheet: '{ws_name}'")
            return worksheet
        except Exception as e:
            logger.error(f"Error getting or creating worksheet '{ws_name}': {e}")
            raise # Re-raise to stop execution if a critical error occurs

    try:
        trade_log_sheet = get_or_create_worksheet(trade_log_ws_name)
        pnl_summary_sheet = get_or_create_worksheet(pnl_summary_ws_name)
        win_ratio_sheet = get_or_create_worksheet(win_ratio_ws_name)

        # --- Log Trade Details ---
        # Concatenate all trade logs into a single DataFrame
        all_trade_logs = []
        for res in results_data:
            if not res['trade_log'].empty:
                all_trade_logs.append(res['trade_log'])
        
        if all_trade_logs:
            trade_log_df = pd.concat(all_trade_logs, ignore_index=True)
            # Convert DataFrame to list of lists for gspread update
            # First row is headers, subsequent rows are data
            trade_log_data = [trade_log_df.columns.values.tolist()] + trade_log_df.values.tolist()
            trade_log_sheet.update(trade_log_data)
            logger.info(f"Updated '{trade_log_ws_name}' with {len(trade_log_df)} trade entries.")
        else:
            logger.info(f"No trade logs to update in '{trade_log_ws_name}'.")
            # Still update headers if no data
            trade_log_sheet.update([['symbol', 'buy_date', 'buy_price', 'sell_date', 'sell_price', 'pnl', 'status']])


        # --- Log P&L Summary ---
        pnl_summary_list = []
        for res in results_data:
            pnl_summary_list.append({
                'Symbol': res['symbol'],
                'Total P&L': res['pnl'],
                'Total Trades': res['total_trades']
            })
        pnl_summary_df = pd.DataFrame(pnl_summary_list)
        
        if not pnl_summary_df.empty:
            pnl_summary_data = [pnl_summary_df.columns.values.tolist()] + pnl_summary_df.values.tolist()
            pnl_summary_sheet.update(pnl_summary_data)
            logger.info(f"Updated '{pnl_summary_ws_name}' with P&L summary.")
        else:
            logger.info(f"No P&L summary data to update in '{pnl_summary_ws_name}'.")
            pnl_summary_sheet.update([['Symbol', 'Total P&L', 'Total Trades']])


        # --- Log Win Ratio ---
        win_ratio_list = []
        for res in results_data:
            win_ratio_list.append({
                'Symbol': res['symbol'],
                'Win Ratio (%)': f"{res['win_ratio']:.2f}", # Format as string with 2 decimal places
                'Wins': res['win_count'],
                'Losses': res['loss_count']
            })
        win_ratio_df = pd.DataFrame(win_ratio_list)

        if not win_ratio_df.empty:
            win_ratio_data = [win_ratio_df.columns.values.tolist()] + win_ratio_df.values.tolist()
            win_ratio_sheet.update(win_ratio_data)
            logger.info(f"Updated '{win_ratio_ws_name}' with win ratio summary.")
        else:
            logger.info(f"No win ratio data to update in '{win_ratio_ws_name}'.")
            win_ratio_sheet.update([['Symbol', 'Win Ratio (%)', 'Wins', 'Losses']])

        logger.info("All Google Sheets updated successfully.")

    except Exception as e:
        logger.error(f"An error occurred during Google Sheets update: {e}")
