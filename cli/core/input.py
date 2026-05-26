# cli/core/input.py
"""Raw key input (Windows)."""

from __future__ import annotations

import sys


def read_key() -> tuple[str, str | None]:
    """
    Returns (kind, code).
    kind: 'enter' | 'esc' | 'arrow' | 'other'
    code: for arrow — 'up'|'down'|'left'|'right'|'pgup'|'pgdn'
    """
    if sys.platform != "win32":
        return "enter", None

    import msvcrt

    ch = msvcrt.getch()
    if ch in (b"\r", b"\n"):
        return "enter", None
    if ch == b"\x1b":
        return "esc", None
    if ch == b"\x03":
        raise KeyboardInterrupt
    if ch in (b"\x00", b"\xe0"):
        ch2 = msvcrt.getch()
        return "arrow", {
            b"H": "up", b"P": "down", b"K": "left", b"M": "right",
            b"I": "pgup", b"Q": "pgdn",
        }.get(ch2, "other")
    return "other", None
