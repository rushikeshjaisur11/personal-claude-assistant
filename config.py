import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

# Directory for persistent data files (reminders, etc.)
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# Comma-separated Telegram user IDs allowed to use the bot (leave empty to allow all)
ALLOWED_USER_IDS: list[int] = [
    int(x) for x in os.environ.get("ALLOWED_USER_IDS", "").split(",") if x.strip()
]
