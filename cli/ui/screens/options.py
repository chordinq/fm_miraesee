# cli/ui/screens/options.py
from __future__ import annotations

from cli.core.frame import build_frame, center_block
from cli.core.input import read_key
from cli.core.presenter import show_frame
from cli.core.terminal import drain_stdin
from cli.theme import BOLD, C_MUTED, C_SKY, C_WHITE, RESET, dim, rgb
from cli.ui.hints import options_hint

_LANGS = [("en", "English"), ("ko", "한국어")]
_current = "en"
_PURPLE = rgb(160, 80, 255)


def get_language() -> str:
    return _current


def _content(focus: int) -> list[str]:
    block = [
        f"{_PURPLE}{BOLD}MIRAESEE{RESET}",
        "",
        f"{BOLD}{C_WHITE}Options{RESET}",
        dim("─" * 28),
        "",
        f"{BOLD}{C_WHITE}Language{RESET}",
        "",
    ]
    for i, (code, label) in enumerate(_LANGS):
        m = "●" if code == _current else "○"
        if i == focus:
            block.append(f"{C_SKY}{BOLD}▶ {m} {label}{RESET}")
        else:
            block.append(f"{C_MUTED}  {m} {label}{RESET}")
    return center_block(block)


def run() -> None:
    global _current
    drain_stdin()
    focus = next((i for i, (c, _) in enumerate(_LANGS) if c == _current), 0)
    while True:
        show_frame(build_frame(_content(focus), options_hint(focus)))
        kind, code = read_key()
        if kind == "arrow" and code == "up":
            focus = (focus - 1) % len(_LANGS)
        elif kind == "arrow" and code == "down":
            focus = (focus + 1) % len(_LANGS)
        elif kind == "enter":
            _current = _LANGS[focus][0]
        elif kind == "esc":
            return
