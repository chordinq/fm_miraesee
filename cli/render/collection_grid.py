# cli/render/collection_grid.py — 5-column collection layout (2 lines per item + row gap)
from __future__ import annotations

from dataclasses import dataclass

from cli.core.ansi import pad_vis, visual_len
from cli.render.align import collection_column_widths
from cli.theme import BOLD, C_MUTED, RESET, Box, rarity_color

COLS = 5
_CELL_GAP = 1


@dataclass(frozen=True)
class CollectionCell:
    name: str
    subtitle: str
    rarity: int
    subtitle_muted: bool = True


def _column_widths() -> list[int]:
    return collection_column_widths(COLS, _CELL_GAP)


def _inner_width(col_widths: list[int] | None = None) -> int:
    widths = col_widths or _column_widths()
    return sum(widths) + (COLS - 1) * _CELL_GAP


def _name_line(cell: CollectionCell, width: int) -> str:
    text = f"{rarity_color(cell.rarity)}{cell.name}{RESET}"
    return pad_vis(text, width, align="c")


def _sub_line(cell: CollectionCell, width: int) -> str:
    text = (
        f"{C_MUTED}{cell.subtitle}{RESET}"
        if cell.subtitle_muted
        else cell.subtitle
    )
    return pad_vis(text, width, align="c")


def _join_row(parts: list[str]) -> str:
    return (" " * _CELL_GAP).join(parts)


def _row_pair(cells: list[CollectionCell], col_widths: list[int]) -> list[str]:
    """One visual row of up to 5 items: name line, level line, blank."""
    slots: list[CollectionCell | None] = list(cells) + [None] * max(0, COLS - len(cells))
    name_parts = [
        _name_line(c, col_widths[i]) if c else " " * col_widths[i]
        for i, c in enumerate(slots[:COLS])
    ]
    sub_parts = [
        _sub_line(c, col_widths[i]) if c else " " * col_widths[i]
        for i, c in enumerate(slots[:COLS])
    ]
    return [_join_row(name_parts), _join_row(sub_parts), ""]


def rounded_box(inner: list[str], content_w: int) -> list[str]:
    """content_w = cell grid width; border spans content_w + 2 (padding inside V)."""
    border = C_MUTED
    border_w = content_w + 2
    top = f"  {border}{Box.TL}{Box.H * border_w}{Box.TR}{RESET}"
    out = [top]
    for ln in inner:
        body = pad_vis(ln, content_w)
        gap = max(0, content_w - visual_len(body))
        out.append(
            f"  {border}{Box.V}{RESET} {body}{' ' * gap} {border}{Box.V}{RESET}"
        )
    out.append(f"  {border}{Box.BL}{Box.H * border_w}{Box.BR}{RESET}")
    return out


_rounded_box = rounded_box  # alias for internal use


def render_collection(
    items: list[CollectionCell],
    *,
    title: str = "Collection",
    col_widths: list[int] | None = None,
) -> list[str]:
    col_widths = col_widths or _column_widths()
    inner_w = _inner_width(col_widths)

    if not items:
        if not title:
            return [f"  {C_MUTED}(empty){RESET}"]
        return [f"  {BOLD}{title}{RESET}", "", f"  {C_MUTED}(empty){RESET}"]

    body: list[str] = []
    for i in range(0, len(items), COLS):
        body.extend(_row_pair(items[i : i + COLS], col_widths))
    if body and body[-1] == "":
        body.pop()

    lines: list[str] = []
    if title:
        lines += [f"  {BOLD}{title}{RESET}", ""]
    lines.extend(rounded_box(body, inner_w))
    return lines
