# cli/core/presenter.py
"""
Single-buffer presenter — one atomic write per frame, no clear() on navigation.
Eliminates blink on tab change / Esc back to main menu.
"""

from __future__ import annotations

import io
import sys

from cli.core.ansi import pad_vis
from cli.core.terminal import hide_cursor, set_theme, term_height, term_width
from constants.colors import RESET


class Presenter:
    def __init__(self) -> None:
        self._ready = False

    def show(self, frame: list[str]) -> None:
        h = term_height()
        w = term_width()

        if not self._ready:
            set_theme()
            self._ready = True

        if len(frame) < h:
            frame = list(frame) + [""] * (h - len(frame))
        elif len(frame) > h:
            frame = frame[:h]

        buf = io.StringIO()
        buf.write("\033[H")
        for i, line in enumerate(frame):
            buf.write("\033[2K\r")
            buf.write(pad_vis(line, w))
            buf.write(RESET)
            if i < h - 1:
                buf.write("\n")
        for _ in range(len(frame), h):
            buf.write("\n")
            buf.write("\033[2K\r")
            buf.write(" " * w)
            buf.write(RESET)
        buf.write("\033[J")  # erase below cursor — no full clear flash
        sys.stdout.write(buf.getvalue())
        hide_cursor()
        sys.stdout.flush()


_presenter = Presenter()


def show_frame(frame: list[str]) -> None:
    _presenter.show(frame)
