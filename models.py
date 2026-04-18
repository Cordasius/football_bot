# bot/models.py
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Tuple


class ResponseStatus(Enum):
    GOING = "going"
    MAYBE = "maybe"
    NOT_GOING = "not_going"


@dataclass
class PlayerResponse:
    user_id: int
    username: str
    first_name: str
    status: ResponseStatus
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Match:
    chat_id: int
    message_id: int
    field_name: str
    date: str
    time: str
    format_str: str
    max_players: int

    players_per_team: int = 0
    total_players_needed: int = 0
    responses: List[PlayerResponse] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        try:
            parts = self.format_str.lower().split("x")
            if len(parts) == 2:
                per_team = int(parts[0])
                self.players_per_team = per_team
                self.total_players_needed = per_team * 2
            else:
                self.total_players_needed = self.max_players
        except Exception:
            self.total_players_needed = self.max_players

    def add_response(
        self,
        user_id: int,
        username: str,
        first_name: str,
        status: ResponseStatus
    ) -> None:
        self.responses = [r for r in self.responses if r.user_id != user_id]
        self.responses.append(
            PlayerResponse(
                user_id=user_id,
                username=username,
                first_name=first_name,
                status=status
            )
        )

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
        return max(0, going - self.total_players_needed)

    def get_main_and_reserve(self) -> Tuple[List[PlayerResponse], List[PlayerResponse]]:
        going_players = self.get_going_players()
        main_players = going_players[: self.total_players_needed]
        reserve_players = going_players[self.total_players_needed :]
        return main_players, reserve_players