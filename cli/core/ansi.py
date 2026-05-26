# cli/core/ansi.py
from __future__ import annotations

import re
import unicodedata

from constants.colors import RESET

_ANSI_RE = re.compile(r"\033\[[0-9;]*m|\033\[\d+m")

try:
    import wcwidth as _wcwidth_mod
except ImportError:
    _wcwidth_mod = None


def _cell_width(ch: str) -> int:
    if len(ch) != 1:
        return 0
    if _wcwidth_mod is not None:
        w = _wcwidth_mod.wcwidth(ch)
        if w >= 0:
            return w
        return 0
    ea = unicodedata.east_asian_width(ch)
    return 2 if ea in ("F", "W") else 1


def _plain(s: str) -> str:
    return _ANSI_RE.sub("", s)


def visual_len(s: str) -> int:
    plain = _plain(s)
    if _wcwidth_mod is not None:
        w = _wcwidth_mod.wcswidth(plain)
        if w is not None and w >= 0:
            return w
    return sum(_cell_width(c) for c in plain)


def _truncate_plain(s: str, max_w: int) -> str:
    out: list[str] = []
    used = 0
    for c in s:
        cw = _cell_width(c)
        if cw <= 0:
            out.append(c)
            continue
        if used + cw > max_w:
            break
        out.append(c)
        used += cw
    return "".join(out)


def pad_vis(text: str, width: int, *, align: str = "l") -> str:
    v = visual_len(text)
    if v > width:
        parts = _ANSI_RE.split(text)
        out: list[str] = []
        used = 0
        for i, part in enumerate(parts):
            if i & 1:
                out.append(part)
            else:
                pw = visual_len(part)
                if used + pw <= width:
                    out.append(part)
                    used += pw
                else:
                    out.append(_truncate_plain(part, width - used))
                    break
        return "".join(out) + RESET
    pad = width - v
    if align == "r":
        return " " * pad + text
    if align == "c":
        l = pad // 2
        return " " * l + text + " " * (pad - l)
    return text + " " * pad
