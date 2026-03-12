"""Entry point — starts the Telegram bot."""

import asyncio
from telegram_bot import run

if __name__ == "__main__":
    asyncio.set_event_loop(asyncio.new_event_loop())
    run()
