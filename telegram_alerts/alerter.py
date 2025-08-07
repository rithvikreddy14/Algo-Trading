# telegram_alerts/alerter.py

import telegram
import logging
import asyncio # New: Import the asyncio library

logger = logging.getLogger(__name__)

def send_alert(message: str, bot_token: str, chat_id: str):
    """
    Sends a message to a predefined Telegram chat using the configured bot.

    Args:
        message (str): The text message to send.
        bot_token (str): The Telegram Bot API token.
        chat_id (str): The numerical chat ID.
    """
    if not bot_token or not chat_id:
        logger.warning("Telegram bot token or chat ID is not configured. Skipping alert.")
        return
        
    try:
        # Initialize the bot with your token
        bot = telegram.Bot(token=bot_token)
        
        # Use asyncio to properly run the asynchronous send_message function
        async def _send_message_async():
            await bot.send_message(chat_id=chat_id, text=message)

        asyncio.run(_send_message_async())
        
        logger.info("Telegram alert sent successfully.")
    except telegram.error.InvalidToken:
        logger.error("Invalid Telegram Bot Token. Please check your config.py.")
    except telegram.error.Unauthorized:
        logger.error("Unauthorized: Bot token is incorrect or bot cannot access the chat. Check chat ID and bot permissions.")
    except telegram.error.NetworkError as e:
        logger.error(f"Network error while sending Telegram alert: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while sending Telegram alert: {e}")
