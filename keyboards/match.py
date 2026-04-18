from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_match_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Иду", callback_data="response_going"),
                InlineKeyboardButton(text="🤔 Под вопросом", callback_data="response_maybe"),
                InlineKeyboardButton(text="❌ Не иду", callback_data="response_not_going"),
            ]
        ]
    )
