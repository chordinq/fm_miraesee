# cli/render/data_table.py — boxed column table (pane-safe width)
from __future__ import annotations

from cli.core.ansi import pad_vis, visual_len
from cli.render.align import _border_inner_max, fit_column_widths
from cli.theme import BOLD, C_MUTED, C_WHITE, RESET, Box


def render_table(
    headers: list[str],
    rows: list[list[str]],
    col_w: list[int] | None = None,
    *,
    weights: list[int] | None = None,
    header_muted: bool = True,
    header_align: str = "l",
    col_align: list[str] | None = None,
) -> list[str]:
    if not rows:
        return [f"  {C_MUTED}(empty){RESET}"]

    inner_max = _border_inner_max()
    if col_w is None:
        w = weights or [1] * len(headers)
        col_w = fit_column_widths(w, inner_max)

    n = len(col_w)
    aligns = (col_align + ["l"] * n)[:n]

    border = C_MUTED
    inner_w = sum(col_w) + 2 * (n - 1)
    border_w = inner_w + 2

    def _cell(text: str, width: int, align: str, *, header: bool = False) -> str:
        t = text
        if header and header_muted:
            t = f"{BOLD}{C_WHITE}{text}{RESET}"
        return pad_vis(t, width, align=align)

    def _row(cells: list[str], *, header: bool = False) -> str:
        parts = []
        for i in range(n):
            c = cells[i] if i < len(cells) else ""
            al = header_align if header else aligns[i]
            parts.append(_cell(c, col_w[i], al, header=header))
        return "  ".join(parts)

    lines: list[str] = [
        f"  {border}{Box.TL}{Box.H * border_w}{Box.TR}{RESET}",
        f"  {border}{Box.V}{RESET} {_row(headers, header=True)} {border}{Box.V}{RESET}",
        f"  {border}{Box.V}{RESET}{' ' * border_w}{border}{Box.V}{RESET}",
    ]
    for cells in rows:
        body = _row(cells)
        gap = max(0, inner_w - visual_len(body))
        lines.append(f"  {border}{Box.V}{RESET} {body}{' ' * gap} {border}{Box.V}{RESET}")
    lines.append(f"  {border}{Box.BL}{Box.H * border_w}{Box.BR}{RESET}")
    return lines
