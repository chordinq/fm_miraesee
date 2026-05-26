# cli/ui/screens/about.py
from __future__ import annotations

from cli.core.frame import build_frame, center_block
from cli.core.input import read_key
from cli.core.presenter import show_frame
from cli.core.terminal import drain_stdin
from cli.theme import BOLD, C_WHITE, RESET, rgb
from cli.ui.hints import about_hint

_PURPLE = rgb(160, 80, 255)
_GREY = rgb(140, 140, 140)


def _content() -> list[str]:
    block = [
        f"{_PURPLE}{BOLD}MIRAESEE{RESET}",
        "",
        f"{_GREY}v1.0.0 · by chordinq{RESET}",
        "",
        f"{C_WHITE}ForgeMaster dump simulator{RESET}",
        f"{C_WHITE}github.com/chordinq/miraesee{RESET}",
    ]
    return center_block(block)


def run() -> None:
    drain_stdin()
    while True:
        show_frame(build_frame(_content(), about_hint()))
        kind, _ = read_key()
        if kind in ("enter", "esc"):
            return
