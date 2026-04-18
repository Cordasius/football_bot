# bot/services/match_service.py
from typing import Dict, Optional

from models import Match, ResponseStatus


# простой in-memory сторедж: chat_id -> Match
_active_matches: Dict[int, Match] = {}


def get_active_match(chat_id: int) -> Optional[Match]:
    """Получить активный матч для чата, если он есть."""
    return _active_matches.get(chat_id)


def has_active_match(chat_id: int) -> bool:
    """Проверить, есть ли уже активный матч в чате."""
    return chat_id in _active_matches


def set_active_match(match: Match) -> None:
    """Сохранить/обновить активный матч для чата."""
    _active_matches[match.chat_id] = match


def cancel_match(chat_id: int) -> Optional[Match]:
    """Отменить матч: удалить его из хранилища и вернуть объект."""
    return _active_matches.pop(chat_id, None)


def add_player_response(
    chat_id: int,
    user_id: int,
    username: str,
    first_name: str,
    status: ResponseStatus,
) -> Optional[Match]:
    """
    Добавить/обновить ответ игрока для матча в чате.
    Возвращает обновлённый Match или None, если матча нет.
    """
    match = get_active_match(chat_id)
    if not match:
        return None

    match.add_response(
        user_id=user_id,
        username=username,
        first_name=first_name,
        status=status,
    )
    return match