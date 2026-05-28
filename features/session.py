# features/session.py — loaded player state from dump text
from __future__ import annotations

from dataclasses import dataclass

from core.game_logic.player_model.PlayerModel import PlayerModel
from utils.parser import parse_dump


@dataclass
class Session:
    player: PlayerModel
    dump_text: str = ""


def session_from_dump(text: str) -> Session | None:
    text = text.strip()
    if not text:
        return None
    try:
        player = parse_dump(text)
    except Exception as exc:
        raise ValueError(f"parse failed: {exc}") from exc
    return Session(player=player, dump_text=text)
