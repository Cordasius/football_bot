from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.match_service import get_active_match, cancel_match
from renderers.match_text import format_match_status

router = Router()


@router.message(Command("status"))
async def cmd_status(message: Message):
    chat_id = message.chat.id

    match = get_active_match(chat_id)
    if not match:
        await message.answer(
            "🤷 В этом чате нет активного матча. "
            "Создайте его командой /new_match"
        )
        return

    status_text = format_match_status(match)
    await message.answer(status_text)


@router.message(Command("cancel_match"))
async def cmd_cancel_match(message: Message):
    chat_id = message.chat.id

    match = cancel_match(chat_id)
    if not match:
        await message.answer("🤷 В этом чате нет активного матча.")
        return

    # можем попытаться удалить карточку матча, но это не обязательно
    try:
        await message.bot.delete_message(chat_id=chat_id, message_id=match.message_id)
    except Exception:
        # карточка могла быть удалена вручную или устареть
        pass

    await message.answer("🗑 Матч отменен.")