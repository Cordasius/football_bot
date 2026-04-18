import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")

if BOT_TOKEN == "your_bot_token_here":
    raise ValueError("⚠️  Using default bot token. Please set BOT_TOKEN in .env file")
