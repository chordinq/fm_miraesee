from __future__ import annotations

from cli.session import Session
from cli.theme import err


def rebuild_session(dump_text: str) -> Session | None:
    from utils.parser import parse_dump
    from core.game_logic.GameLogic import GameLogic

    try:
        player = parse_dump(dump_text)
        gl = GameLogic(player)
    except Exception as e:
        print(err(f"  Parse error: {e}"))
        return None

    session = Session(player=player, game_logic=gl, dump_raw=dump_text)
    try:
        from cli.store.database import open_db
        session.db = open_db()
    except Exception:
        session.db = None
    return session
