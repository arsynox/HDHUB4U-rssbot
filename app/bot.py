import os
import time
import logging
import telegram
from app.scraper import fetch_latest_items

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SCRAPE_INTERVAL_SECONDS = int(os.getenv("SCRAPE_INTERVAL_SECONDS", 3600))

bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

def send_telegram_message(text):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text, disable_web_page_preview=False)
        logger.info(f"Sent message: {text}")
    except Exception as e:
        logger.error(f"Failed to send message: {e}")

def main():
    logger.info("HDHub4u Telegram bot started.")
    while True:
        try:
            new_items = fetch_latest_items()
            for item in new_items:
                message = f"New Release: {item['title']}\n{item['link']}"
                send_telegram_message(message)
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        time.sleep(SCRAPE_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
