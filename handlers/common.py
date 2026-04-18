from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🤖 Бот для организации футбольных матчей!\n\n"
        "Доступные команды:\n"
        "/new_match место; дата; время; формат\n"
        "Например:\n"
        "/new_match Тульская; 25.04; 19:00; 8x8\n\n"
        "/status - показать текущий состав\n"
        "/cancel_match - отменить текущий матч"
    )
