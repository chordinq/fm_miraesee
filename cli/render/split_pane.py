# cli/render/split_pane.py — two-column content lines for hub pane
from __future__ import annotations

from cli.core.ansi import pad_vis, visual_len
from cli.core.terminal import term_width
from cli.theme import BOLD, C_MUTED, RESET

LEFT_NAV = 16
_SEP = 3


def hub_pane_width() -> int:
    return max(40, term_width() - LEFT_NAV - _SEP)


def merge_columns(
    left: list[str],
    right: list[str],
    *,
    left_w: int | None = None,
    right_w: int | None = None,
) -> list[str]:
    pane = hub_pane_width()
    lw = left_w or max(20, pane * 38 // 100)
    rw = right_w or max(20, pane - lw - 3)
    sep = f" {C_MUTED}│{RESET} "
    h = max(len(left), len(right))
    out: list[str] = []
    for i in range(h):
        l = left[i] if i < len(left) else ""
        r = right[i] if i < len(right) else ""
        out.append(pad_vis(l, lw) + sep + pad_vis(r, rw))
    return out


def section_titles(left_title: str = "Result", right_title: str = "Detailed") -> list[str]:
    pane = hub_pane_width()
    lw = max(20, pane * 38 // 100)
    rw = max(20, pane - lw - 3)
    sep = f" {C_MUTED}│{RESET} "
    lt = f"{BOLD}{left_title}{RESET}"
    rt = f"{BOLD}{right_title}{RESET}"
    return [pad_vis(lt, lw) + sep + pad_vis(rt, rw)]
