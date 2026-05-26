# cli/core/frame.py
"""Layout: footer hint line + body centring."""

from __future__ import annotations

from cli.core.ansi import pad_vis, visual_len  # visual_len: terminal cell width (wcwidth)
from cli.core.terminal import term_height, term_width
from cli.theme import dim
from constants.colors import RESET

FOOTER_ROWS = 1

GUIDE_DUMP = "Paste HEX dump here."


def footer_line(text: str, width: int | None = None) -> list[str]:
    """Single centered footer line (no extra blank row)."""
    w = width or term_width()
    return [pad_vis(dim(text), w, align="c")]


def blank_line(width: int | None = None) -> str:
    """Full-width cleared row (spaces + RESET) for fit_body padding."""
    w = width or term_width()
    return pad_vis("", w) + RESET


def center_block(lines: list[str], width: int | None = None) -> list[str]:
    """Center a text block: equal inner width, then center in terminal."""
    w = width or term_width()
    if not lines:
        return []
    inner_w = max(visual_len(ln) for ln in lines)
    block = [pad_vis(ln, inner_w, align="l") for ln in lines]
    return [pad_vis(ln, w, align="c") + RESET for ln in block]


def body_height(*, header_rows: int = 0) -> int:
    return max(1, term_height() - header_rows - FOOTER_ROWS)


def fit_body(content: list[str], area_h: int, *, center: bool = True) -> list[str]:
    w = term_width()
    if not center:
        body = list(content[:area_h])
        while len(body) < area_h:
            body.append(blank_line(w))
        return body
    if len(content) >= area_h:
        return content[:area_h]
    top = (area_h - len(content)) // 2
    body = [blank_line(w)] * top + list(content)
    while len(body) < area_h:
        body.append(blank_line(w))
    return body


def clip_pane(lines: list[str], pane_w: int, pane_h: int, scroll: int = 0) -> list[str]:
    out: list[str] = []
    for ln in lines[scroll : scroll + pane_h]:
        v = visual_len(ln)
        if v > pane_w:
            out.append(pad_vis(ln, pane_w))
        elif v < pane_w:
            out.append(ln + " " * (pane_w - v))
        else:
            out.append(ln)
    while len(out) < pane_h:
        out.append(" " * pane_w)
    return out


def build_frame(
    content: list[str],
    footer: str,
    *,
    header: list[str] | None = None,
    center: bool = True,
) -> list[str]:
    h = term_height()
    w = term_width()
    hdr = header or []
    area = max(0, h - len(hdr) - FOOTER_ROWS)
    body = fit_body(content, area, center=center)
    return hdr + body + footer_line(footer, w)
