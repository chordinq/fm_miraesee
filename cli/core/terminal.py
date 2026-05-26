# cli/core/terminal.py
"""Low-level terminal control."""

from __future__ import annotations

import shutil
import sys
from contextlib import contextmanager

from constants.colors import BG_HEX, FG_HEX


def term_size() -> tuple[int, int]:
    try:
        c, l = shutil.get_terminal_size((100, 24))
        return c, l
    except OSError:
        return 100, 24


def term_width() -> int:
    return term_size()[0]


def term_height() -> int:
    return term_size()[1]


def set_theme() -> None:
    bg = BG_HEX.lstrip("#")
    fg = FG_HEX.lstrip("#")
    sys.stdout.write(f"\033]10;#{fg}\033\\")
    sys.stdout.write(f"\033]11;#{bg}\033\\")
    sys.stdout.flush()


def hide_cursor() -> None:
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()


def show_cursor() -> None:
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()


def enter_alt() -> None:
    sys.stdout.write("\033[?1049h\033[H")
    set_theme()
    sys.stdout.flush()


def leave_alt() -> None:
    sys.stdout.write("\033[?1049l")
    sys.stdout.flush()


def drain_stdin(ms: int = 80) -> None:
    if sys.platform != "win32":
        return
    import msvcrt
    import time
    end = time.monotonic() + ms / 1000.0
    while time.monotonic() < end:
        while msvcrt.kbhit():
            msvcrt.getch()
        time.sleep(0.01)


@contextmanager
def ui_session():
    """Hold alternate screen for entire menu session (no scrollback scrollbar)."""
    drain_stdin()
    enter_alt()
    hide_cursor()
    try:
        yield
    finally:
        show_cursor()
        leave_alt()
