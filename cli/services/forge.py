from __future__ import annotations


def run_forge(session, count: int):
    return session.game_logic.forge(count)
