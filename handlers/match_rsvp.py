# bot/handlers/match_rsvp.py
import logging

from aiogram import Router, F
from aiogram.types import CallbackQuery

from models import ResponseStatus
from services.match_service import add_player_response, get_active_match
from renderers.match_text import format_match_text
from keyboards.match import get_match_keyboard

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data.startswith("response_"))
async def process_response(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    username = callback.from_user.username or ""
    first_name = callback.from_user.first_name or "Пользователь"

    # определяем статус из callback_data
    response_type = callback.data.split("_", maxsplit=1)[1]
    if response_type == "going":
        status = ResponseStatus.GOING
    elif response_type == "maybe":
        status = ResponseStatus.MAYBE
    elif response_type == "not_going":
        status = ResponseStatus.NOT_GOING
    else:
        await callback.answer("Неизвестный тип ответа.")
        return

    match = add_player_response(chat_id, user_id, username, first_name, status)
    if not match:
        await callback.answer("Матч не найден или был отменен.")
        return

    updated_text = format_match_text(match)
    keyboard = get_match_keyboard()

    try:
        await callback.message.edit_text(
            text=updated_text,
            reply_markup=keyboard
        )

        status_texts = {
            ResponseStatus.GOING: "✅ Вы идете на матч!",
            ResponseStatus.MAYBE: "🤔 Вы под вопросом.",
            ResponseStatus.NOT_GOING: "❌ Вы не идете на матч.",
        }
        await callback.answer(status_texts[status])

    except Exception as e:
        logger.error(f"Error updating match message: {e}")
        await callback.answer("Ошибка обновления сообщения.")