# Football Boot - Telegram Bot for Football Match Organization

Telegram bot for organizing football matches with RSVP functionality, player limits, and waitlists.

## Features

- **One active match per chat** - Simple management
- **Match creation** with `/new_match` command
- **Interactive buttons** - ✅ Иду, 🤔 Под вопросом, ❌ Не иду
- **Auto-updating match card** - Real-time updates via inline buttons
- **Player limit and waitlist** - Automatic waitlist when player limit reached
- **Match status** - `/status` command to view current lineup
- **Match cancellation** - `/cancel_match` to remove active match

## User Flow

1. Admin sends `/new_match` in group chat
2. Bot asks for match parameters:
   - Field/location
   - Date
   - Time
   - Match format (e.g., 8x8, 6x6, 5x5)
3. Bot publishes match card with inline buttons
4. Players click buttons to RSVP
5. Bot updates the same message with:
   - Who's going
   - Who's maybe
   - Who's not going
   - Remaining spots
   - Waitlist (if any)

## Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd football_boot
```

### 2. Create virtual environment (optional but recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure bot token

#### Get a bot token from BotFather:
1. Open Telegram, search for `@BotFather`
2. Send `/newbot` and follow instructions
3. Copy the bot token (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### Set up environment:
```bash
cp .env.example .env
# Edit .env file and replace 'your_bot_token_here' with your actual token
```

### 5. Run the bot
```bash
python bot.py
```

## Commands

- `/start` - Show welcome message and available commands
- `/new_match` - Create a new match (admin only in groups)
- `/status` - Show current match status and player list
- `/cancel_match` - Cancel the active match (admin only)

## Match Format

The format determines the number of players needed:
- `8x8` = 8 players per team → 16 total players needed
- `6x6` = 6 players per team → 12 total players needed
- `5x5` = 5 players per team → 10 total players needed

The bot automatically calculates player requirements based on the format.

## Data Storage

⚠️ **Important**: This MVP version uses **in-memory storage**. All data is lost when the bot restarts.

For production use, you should implement persistent storage (SQLite, PostgreSQL, etc.).

## Project Structure

```
football_boot/
├── bot.py              # Main bot application
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (gitignored)
├── .env.example       # Example environment variables
├── .gitignore         # Git ignore file
└── README.md          # This file
```

## Development

### Dependencies
- `aiogram==3.0.0b7` - Async Telegram Bot Framework
- `python-dotenv==1.0.0` - Environment variable management

### Adding Persistent Storage

To add database support, consider:
1. **SQLite** for simple local storage
2. **PostgreSQL** for production
3. **Redis** for caching + persistence

Example SQLite integration:
```python
import sqlite3
from contextlib import closing

def init_db():
    with closing(sqlite3.connect('matches.db')) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                chat_id INTEGER PRIMARY KEY,
                message_id INTEGER,
                field TEXT,
                date TEXT,
                time TEXT,
                format TEXT,
                max_players INTEGER,
                created_at TIMESTAMP
            )
        ''')
        # Add players table similarly
```

## License

MIT

## Support

For issues and feature requests, please open an issue in the repository.