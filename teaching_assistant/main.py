"""Entry point for Teaching Assistant Bot."""
import asyncio
import logging
import os
from dotenv import load_dotenv

load_dotenv()

from teaching_assistant.bot import Bot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("teaching-assistant")

async def main():
    """Run the bot."""
    logger.info("Starting Teaching Assistant Bot...")
    bot = Bot()
    await bot.run()

def main_sync():
    """Synchronous entry point."""
    asyncio.run(main())

if __name__ == "__main__":
    main_sync()