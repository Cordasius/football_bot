import os
from dotenv import load_dotenv

load_dotenv()
bot_token = os.getenv("BOT_TOKEN", "your_bot_token_here")

if bot_token == "your_bot_token_here":
    raise ValueError("⚠️  Using default bot token. Please set BOT_TOKEN in .env file")
