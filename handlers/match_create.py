from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from models import Match
from services.match_service import has_active_match, set_active_match
from keyboards.match import get_match_keyboard
from renderers.match_text import format_match_text

router = Router()


def parse_new_match_args(args: str) -> tuple[str, str, str, str]:
    """
    Ожидаем строку вида:
    '<место>; <дата>; <время>; <формат>'
    Например: 'Манеж Динамо; 25.04; 19:00; 8x8'
    """
    parts = [p.strip() for p in args.split(";")]
    if len(parts) != 4:
        raise ValueError(
            "Нужно указать: место; дату; время; формат.\n"
            "Например:\n"
            "/new_match Тульская; 25.04; 19:00; 8x8"
        )

    field, date, time, format_str = parts
    if "x" not in format_str.lower():
        raise ValueError("Формат должен быть вида 8x8, 6x6, 5x5 и т.п.")

    return field, date, time, format_str


@router.message(Command("new_match"))
async def cmd_new_match(message: Message, command: CommandObject):
    chat_id = message.chat.id

    if has_active_match(chat_id):
        await message.answer(
            "⚠️ В этом чате уже есть активный матч. "
            "Используйте /cancel_match чтобы отменить его."
        )
        return

    # если аргументов нет — подсказка по формату
    if not command.args:
        await message.answer(
            "Укажи параметры матча в одной строке через ';':\n"
            "/new_match <место>; <дата>; <время>; <формат>\n"
            "Например:\n"
            "/new_match Манеж Динамо; 25.04; 19:00; 8x8"
        )
        return

    try:
        field, date, time, format_str = parse_new_match_args(command.args)

        # создаём матч (id сообщения пока 0, обновим после send)
        match = Match(
            chat_id=chat_id,
            message_id=0,
            field_name=field,
            date=date,
            time=time,
            format_str=format_str,
            max_players=0,  # не важен, __post_init__ сам посчитает total_players_needed
        )

        text = format_match_text(match)
        keyboard = get_match_keyboard()

        sent = await message.answer(text, reply_markup=keyboard)
        match.message_id = sent.message_id

        set_active_match(match)

        await message.answer("✅ Матч создан! Игроки могут нажимать кнопки в карточке выше.")

    except ValueError as e:
        await message.answer(f"❌ {e}")
    except Exception:
        await message.answer("❌ Произошла внутренняя ошибка при создании матча.")