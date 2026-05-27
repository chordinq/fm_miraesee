# ui/services/display_level.py — dump-stored level → UI level (+1)
from __future__ import annotations


def display_level(dump_level: int) -> int:
    """In-game dump stores level - 1; UI shows dump + 1."""
    return int(dump_level) + 1


def format_level(dump_level: int) -> str:
    return f"Lv.{display_level(dump_level)}"
