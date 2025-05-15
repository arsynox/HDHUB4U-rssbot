# app/bot.py
import os
import logging
from telegram.ext import Application, ContextTypes
from scraper import Hdhub4uScraper

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class MonitoringBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.interval = int(os.getenv('SCRAPE_INTERVAL_SECONDS', 3600))
        self.scraper = Hdhub4uScraper()

    async def check_updates(self, context: ContextTypes.DEFAULT_TYPE):
        new_items = self.scraper.scrape_new_releases()
        for item in new_items:
            message = f"🎬 New Release: {item['title']}\n🔗 {item['link']}"
            await context.bot.send_message(
                chat_id=self.chat_id,
                text=message
            )

    def run(self):
        application = Application.builder().token(self.token).build()
        job_queue = application.job_queue
        job_queue.run_repeating(
            self.check_updates,
            interval=self.interval,
            first=10
        )
        application.run_polling()

if __name__ == '__main__':
    bot = MonitoringBot()
    bot.run()
