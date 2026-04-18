import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup,
    InlineKeyboardButton, ReplyKeyboardRemove
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== Data Models ==========

class ResponseStatus(Enum):
    GOING = "going"
    MAYBE = "maybe"
    NOT_GOING = "not_going"

class PlayerResponse:
    def __init__(self, user_id: int, username: str, first_name: str, status: ResponseStatus):
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.status = status
        self.timestamp = datetime.now()

class Match:
    def __init__(self, chat_id: int, message_id: int, field: str, date: str, time: str,
                 format_str: str, max_players: int):
        self.chat_id = chat_id
        self.message_id = message_id
        self.field = field
        self.date = date
        self.time = time
        self.format_str = format_str  # e.g., "8x8", "6x6"
        self.max_players = max_players

        # Calculate total players needed based on format
        # For example, "8x8" means 8 players per team, total 16
        try:
            parts = format_str.split('x')
            if len(parts) == 2:
                per_team = int(parts[0])
                self.players_per_team = per_team
                self.total_players_needed = per_team * 2
            else:
                self.players_per_team = 0
                self.total_players_needed = max_players
        except:
            self.players_per_team = 0
            self.total_players_needed = max_players

        self.responses: List[PlayerResponse] = []
        self.created_at = datetime.now()

    def add_response(self, user_id: int, username: str, first_name: str, status: ResponseStatus):
        # Remove existing response from this user
        self.responses = [r for r in self.responses if r.user_id != user_id]

        # Add new response
        self.responses.append(PlayerResponse(user_id, username, first_name, status))

    def get_going_players(self) -> List[PlayerResponse]:
        return [r for r in self.responses if r.status == ResponseStatus.GOING]

    def get_maybe_players(self) -> List[PlayerResponse]:
        return [r for r in self.responses if r.status == ResponseStatus.MAYBE]

    def get_not_going_players(self) -> List[PlayerResponse]:
        return [r for r in self.responses if r.status == ResponseStatus.NOT_GOING]

    def get_player_count(self) -> Tuple[int, int, int]:
        going = len(self.get_going_players())
        maybe = len(self.get_maybe_players())
        not_going = len(self.get_not_going_players())
        return going, maybe, not_going

    def get_waitlist_count(self) -> int:
        going = len(self.get_going_players())
        if going > self.total_players_needed:
            return going - self.total_players_needed
        return 0

# ========== State Management ==========

class CreateMatchStates(StatesGroup):
    waiting_field = State()
    waiting_date = State()
    waiting_time = State()
    waiting_format = State()

# Global storage (in-memory)
active_matches: Dict[int, Match] = {}  # chat_id -> Match

# ========== Bot Setup ==========

router = Router()

# ========== Handlers ==========

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🤖 Бот для организации футбольных матчей!\n\n"
        "Доступные команды:\n"
        "/new_match - создать новый матч\n"
        "/status - показать текущий состав\n"
        "/cancel_match - отменить текущий матч"
    )

@router.message(Command("new_match"))
async def cmd_new_match(message: Message, state: FSMContext):
    chat_id = message.chat.id

    # Check if there's already an active match in this chat
    if chat_id in active_matches:
        await message.answer("⚠️ В этом чате уже есть активный матч. Используйте /cancel_match чтобы отменить его.")
        return

    await message.answer(
        "🏟 Создание нового матча.\n\n"
        "Шаг 1/4: Укажите место проведения (поле):",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(CreateMatchStates.waiting_field)

@router.message(CreateMatchStates.waiting_field)
async def process_field(message: Message, state: FSMContext):
    await state.update_data(field=message.text)
    await message.answer("📅 Шаг 2/4: Укажите дату матча (например, 25.04.2024):")
    await state.set_state(CreateMatchStates.waiting_date)

@router.message(CreateMatchStates.waiting_date)
async def process_date(message: Message, state: FSMContext):
    await state.update_data(date=message.text)
    await message.answer("⏰ Шаг 3/4: Укажите время матча (например, 19:00):")
    await state.set_state(CreateMatchStates.waiting_time)

@router.message(CreateMatchStates.waiting_time)
async def process_time(message: Message, state: FSMContext):
    await state.update_data(time=message.text)
    await message.answer("👥 Шаг 4/4: Укажите формат матча (например, 8x8, 6x6, 5x5):")
    await state.set_state(CreateMatchStates.waiting_format)

@router.message(CreateMatchStates.waiting_format)
async def process_format(message: Message, state: FSMContext, bot: Bot):
    chat_id = message.chat.id
    format_str = message.text.strip()

    # Parse format to determine player count
    try:
        parts = format_str.split('x')
        if len(parts) != 2:
            raise ValueError("Некорректный формат. Используйте например: 8x8")

        per_team = int(parts[0])
        total_players_needed = per_team * 2

        # Get data from state
        data = await state.get_data()
        field = data.get('field', 'Не указано')
        date = data.get('date', 'Не указано')
        time = data.get('time', 'Не указано')

        # Create match card message
        match_text = format_match_text(field, date, time, format_str, total_players_needed)

        # Create inline keyboard
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Иду", callback_data="response_going"),
                InlineKeyboardButton(text="🤔 Под вопросом", callback_data="response_maybe"),
                InlineKeyboardButton(text="❌ Не иду", callback_data="response_not_going")
            ]
        ])

        # Send match card
        sent_message = await bot.send_message(
            chat_id=chat_id,
            text=match_text,
            reply_markup=keyboard
        )

        # Create and store match object
        match = Match(
            chat_id=chat_id,
            message_id=sent_message.message_id,
            field=field,
            date=date,
            time=time,
            format_str=format_str,
            max_players=total_players_needed
        )
        active_matches[chat_id] = match

        await message.answer("✅ Матч создан! Игроки могут нажимать кнопки ниже.")

    except ValueError as e:
        await message.answer(f"❌ Ошибка: {str(e)}\nУкажите формат правильно (например, 8x8):")
        return
    except Exception as e:
        logger.error(f"Error creating match: {e}")
        await message.answer("❌ Произошла ошибка при создании матча.")
        return
    finally:
        await state.clear()

@router.message(Command("status"))
async def cmd_status(message: Message):
    chat_id = message.chat.id

    if chat_id not in active_matches:
        await message.answer("🤷 В этом чате нет активного матча. Создайте его командой /new_match")
        return

    match = active_matches[chat_id]
    status_text = format_match_status(match)
    await message.answer(status_text, parse_mode="HTML")

@router.message(Command("cancel_match"))
async def cmd_cancel_match(message: Message, bot: Bot):
    chat_id = message.chat.id

    if chat_id not in active_matches:
        await message.answer("🤷 В этом чате нет активного матча.")
        return

    # Delete match message
    match = active_matches[chat_id]
    try:
        await bot.delete_message(chat_id=chat_id, message_id=match.message_id)
    except:
        pass

    # Remove from storage
    del active_matches[chat_id]
    await message.answer("🗑 Матч отменен.")

@router.callback_query(F.data.startswith("response_"))
async def process_response(callback: CallbackQuery, bot: Bot):
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    username = callback.from_user.username or ""
    first_name = callback.from_user.first_name or "Пользователь"

    if chat_id not in active_matches:
        await callback.answer("Матч не найден или был отменен.")
        return

    match = active_matches[chat_id]

    # Parse response type
    response_type = callback.data.split("_")[1]
    if response_type == "going":
        status = ResponseStatus.GOING
    elif response_type == "maybe":
        status = ResponseStatus.MAYBE
    elif response_type == "not_going":
        status = ResponseStatus.NOT_GOING
    else:
        await callback.answer("Неизвестный тип ответа.")
        return

    # Update player response
    match.add_response(user_id, username, first_name, status)

    # Update match message
    updated_text = format_match_text(
        match.field, match.date, match.time,
        match.format_str, match.total_players_needed,
        match
    )

    # Create updated keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Иду", callback_data="response_going"),
            InlineKeyboardButton(text="🤔 Под вопросом", callback_data="response_maybe"),
            InlineKeyboardButton(text="❌ Не иду", callback_data="response_not_going")
        ]
    ])

    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=match.message_id,
            text=updated_text,
            reply_markup=keyboard
        )

        # Send confirmation to user
        status_texts = {
            ResponseStatus.GOING: "✅ Вы идете на матч!",
            ResponseStatus.MAYBE: "🤔 Вы под вопросом.",
            ResponseStatus.NOT_GOING: "❌ Вы не идете на матч."
        }
        await callback.answer(status_texts[status])

    except Exception as e:
        logger.error(f"Error updating message: {e}")
        await callback.answer("Ошибка обновления.")

# ========== Helper Functions ==========

def format_match_text(field: str, date: str, time: str, format_str: str,
                      total_players: int, match: Optional[Match] = None) -> str:
    """Format match card text"""
    base_text = (
        f"🏟 <b>Футбольный матч</b>\n\n"
        f"📍 Место: {field}\n"
        f"📅 Дата: {date}\n"
        f"⏰ Время: {time}\n"
        f"👥 Формат: {format_str}\n"
        f"🎯 Игроков нужно: {total_players}\n"
    )

    if match:
        going, maybe, not_going = match.get_player_count()
        waitlist = match.get_waitlist_count()

        players_text = (
            f"\n📊 <b>Статистика:</b>\n"
            f"✅ Идут: {going}/{total_players}\n"
            f"🤔 Под вопросом: {maybe}\n"
            f"❌ Не идут: {not_going}\n"
        )

        if waitlist > 0:
            players_text += f"⏳ В листе ожидания: {waitlist}\n"

        # Add player lists
        if match.responses:
            players_text += "\n<b>Состав:</b>\n"

            going_players = match.get_going_players()
            if going_players:
                players_text += "\n✅ <b>Идут:</b>\n"
                for i, player in enumerate(going_players[:total_players], 1):
                    players_text += f"{i}. {format_player_name(player)}\n"

                # Waitlist players
                if len(going_players) > total_players:
                    players_text += "\n⏳ <b>Лист ожидания:</b>\n"
                    for i, player in enumerate(going_players[total_players:], total_players + 1):
                        players_text += f"{i}. {format_player_name(player)}\n"

            maybe_players = match.get_maybe_players()
            if maybe_players:
                players_text += "\n🤔 <b>Под вопросом:</b>\n"
                for i, player in enumerate(maybe_players, 1):
                    players_text += f"{i}. {format_player_name(player)}\n"

            not_going_players = match.get_not_going_players()
            if not_going_players:
                players_text += "\n❌ <b>Не идут:</b>\n"
                for i, player in enumerate(not_going_players, 1):
                    players_text += f"{i}. {format_player_name(player)}\n"

        base_text += players_text

    base_text += "\n👇 Нажмите кнопку чтобы отметить свое участие!"
    return base_text

def format_match_status(match: Match) -> str:
    """Format detailed match status"""
    going, maybe, not_going = match.get_player_count()
    waitlist = match.get_waitlist_count()

    text = (
        f"<b>Текущий статус матча:</b>\n\n"
        f"📍 Место: {match.field}\n"
        f"📅 Дата: {match.date}\n"
        f"⏰ Время: {match.time}\n"
        f"👥 Формат: {match.format_str}\n"
        f"🎯 Игроков нужно: {match.total_players_needed}\n\n"
        f"📊 <b>Статистика:</b>\n"
        f"✅ Идут: {going}/{match.total_players_needed}\n"
        f"🤔 Под вопросом: {maybe}\n"
        f"❌ Не идут: {not_going}\n"
    )

    if waitlist > 0:
        text += f"⏳ В листе ожидания: {waitlist}\n"

    # Player lists
    if match.responses:
        text += "\n<b>Состав:</b>\n"

        going_players = match.get_going_players()
        if going_players:
            text += "\n✅ <b>Идут:</b>\n"
            for i, player in enumerate(going_players[:match.total_players_needed], 1):
                text += f"{i}. {format_player_name(player)}\n"

            if len(going_players) > match.total_players_needed:
                text += "\n⏳ <b>Лист ожидания:</b>\n"
                for i, player in enumerate(going_players[match.total_players_needed:], match.total_players_needed + 1):
                    text += f"{i}. {format_player_name(player)}\n"

        maybe_players = match.get_maybe_players()
        if maybe_players:
            text += "\n🤔 <b>Под вопросом:</b>\n"
            for i, player in enumerate(maybe_players, 1):
                text += f"{i}. {format_player_name(player)}\n"

    return text

def format_player_name(player: PlayerResponse) -> str:
    """Format player name for display"""
    if player.username:
        return f"@{player.username}"
    return player.first_name

# ========== Main Function ==========

async def main():
    # Load environment variables
    from dotenv import load_dotenv
    import os

    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN", "your_bot_token_here")

    if bot_token == "your_bot_token_here":
        logger.warning("⚠️  Using default bot token. Please set BOT_TOKEN in .env file")

    # Initialize bot and dispatcher
    bot = Bot(token=bot_token)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(router)

    # Start polling
    logger.info("🤖 Bot starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())