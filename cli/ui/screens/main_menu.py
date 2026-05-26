# cli/ui/screens/main_menu.py
from __future__ import annotations

from cli.core.frame import build_frame, center_block
from cli.core.input import read_key
from cli.core.presenter import show_frame
from cli.core.terminal import drain_stdin
from cli.ui.hints import main_menu_hint
from cli.theme import BOLD, C_MUTED, C_SKY, RESET, rgb

# (action key, display label)
ITEMS = [
    ("run", "RUN"),
    ("options", "OPTION"),
    ("about", "ABOUT"),
    ("exit", "EXIT"),
]

_BANNER = [
    "███╗   ███╗██╗██████╗  █████╗ ███████╗███████╗███████╗███████╗",
    "████╗ ████║██║██╔══██╗██╔══██╗██╔════╝██╔════╝██╔════╝██╔════╝",
    "██╔████╔██║██║██████╔╝███████║█████╗  ███████╗█████╗  █████╗  ",
    "██║╚██╔╝██║██║██╔══██╗██╔══██║██╔══╝  ╚════██║██╔══╝  ██╔══╝  ",
    "██║ ╚═╝ ██║██║██║  ██║██║  ██║███████╗███████║███████╗███████╗",
    "╚═╝     ╚═╝╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚══════╝",
]
_PURPLE = rgb(160, 80, 255)
_GREY = rgb(140, 140, 140)


def _menu_lines(focus: int) -> list[str]:
    out: list[str] = []
    for i, (_, label) in enumerate(ITEMS):
        if i == focus:
            out.append(f"{C_SKY}{BOLD}▶ {label}{RESET}")
        else:
            out.append(f"{C_MUTED}  {label}{RESET}")
    return out


def _content(focus: int) -> list[str]:
    block: list[str] = []
    for ln in _BANNER:
        block.append(f"{_PURPLE}{ln}{RESET}")
    block.append(f"{_GREY}v1.0.0 · by chordinq{RESET}")
    block.append("")
    block.extend(_menu_lines(focus))
    return center_block(block)


def run() -> str:
    drain_stdin()
    focus = 0
    while True:
        show_frame(build_frame(_content(focus), main_menu_hint(focus)))
        kind, code = read_key()
        if kind == "arrow" and code == "up":
            focus = (focus - 1) % len(ITEMS)
        elif kind == "arrow" and code == "down":
            focus = (focus + 1) % len(ITEMS)
        elif kind == "enter":
            return ITEMS[focus][0]
        elif kind == "esc":
            continue
