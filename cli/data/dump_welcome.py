# cli/data/dump_welcome.py
from __future__ import annotations

import os
import sys

from cli.core.ansi import pad_vis, visual_len
from cli.core.frame import GUIDE_DUMP, build_frame
from cli.core.terminal import term_width
from cli.theme import RESET, rgb

_BANNER = [
    "███╗   ███╗██╗██████╗  █████╗ ███████╗███████╗███████╗███████╗",
    "████╗ ████║██║██╔══██╗██╔══██╗██╔════╝██╔════╝██╔════╝██╔════╝",
    "██╔████╔██║██║██████╔╝███████║█████╗  ███████╗█████╗  █████╗  ",
    "██║╚██╔╝██║██║██╔══██╗██╔══██║██╔══╝  ╚════██║██╔══╝  ██╔══╝  ",
    "██║ ╚═╝ ██║██║██║  ██║██║  ██║███████╗███████║███████╗███████╗",
    "╚═╝     ╚═╝╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚══════╝",
]


def _center_line(line: str, width: int) -> str:
    pad = max(0, (width - visual_len(line)) // 2)
    return " " * pad + line


def welcome_lines() -> list[str]:
    w = term_width()
    p = rgb(160, 80, 255)
    g = rgb(140, 140, 140)
    out = [_center_line(f"{p}{ln}{RESET}", w) for ln in _BANNER]
    out += [
        "",
        _center_line(f"{g}v1.0.0 · by chordinq{RESET}", w),
        "",
    ]
    return out


def _clear_screen() -> None:
    if sys.platform == "win32":
        os.system("cls")
    else:
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()


def show_dump_screen() -> None:
    """Normal-screen welcome (no alt buffer — avoids overlap with input())."""
    _clear_screen()
    w = term_width()
    for line in build_frame(welcome_lines(), GUIDE_DUMP):
        print(pad_vis(line, w))
