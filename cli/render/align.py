# cli/render/align.py — shared column alignment for pane width
from __future__ import annotations

from cli.core.ansi import pad_vis, visual_len
from cli.render.split_pane import hub_pane_width

COLS_5 = 5


def pane_content_width() -> int:
    """Max visual width for hub right-pane lines (incl. leading indent)."""
    return max(30, hub_pane_width())


def collection_inner_max() -> int:
    """Inner grid width inside rounded box: '  ' + borders + body <= pane."""
    return max(20, hub_pane_width() - 6)


def collection_column_widths(cols: int = COLS_5, gap: int = 1) -> list[int]:
    """Column widths that fill the collection box (remainder spread left→right)."""
    inner = collection_inner_max()
    gaps = gap * max(0, cols - 1)
    budget = max(cols * 3, inner - gaps)
    base, extra = divmod(budget, cols)
    return [base + (1 if i < extra else 0) for i in range(cols)]


def five_column_widths(cols: int = COLS_5, gap: int = 1) -> int:
    """Uniform cell width (legacy); prefer collection_column_widths for full-width grid."""
    return max(collection_column_widths(cols, gap))


def fit_column_widths(weights: list[int], max_inner: int, mins: list[int] | None = None) -> list[int]:
    """Scale integer weights to sum to max_inner (column gaps excluded)."""
    gap = 2 * (len(weights) - 1)
    budget = max_inner - gap
    if budget <= 0:
        return [3] * len(weights)
    total = sum(weights)
    if total <= budget:
        out = list(weights)
    else:
        out = [max(3, int(w * budget / total)) for w in weights]
    if mins:
        for i, m in enumerate(mins):
            if i < len(out):
                out[i] = max(out[i], m)
    # trim if over budget after mins
    while sum(out) + gap > max_inner and max(out) > 3:
        i = out.index(max(out))
        out[i] -= 1
    return out


def grid_row_5(cells: list[str], col_widths: list[int] | None = None, *, gap: int = 1) -> str:
    widths = col_widths or collection_column_widths(COLS_5, gap)
    slots = cells + [""] * max(0, COLS_5 - len(cells))
    parts = [
        pad_vis(c, widths[i], align="c") if c else " " * widths[i]
        for i, c in enumerate(slots[:COLS_5])
    ]
    return (" " * gap).join(parts)


def grid_rows_5(items: list[str]) -> list[str]:
    rows: list[str] = []
    for i in range(0, len(items), COLS_5):
        rows.append(grid_row_5(items[i : i + COLS_5]))
    return rows


def line_fits_pane(line: str, extra_indent: int = 0) -> bool:
    return visual_len(line) <= pane_content_width() + extra_indent


def table_cols_with_stats(
    fixed_widths: list[int],
    stat_cols: int = 2,
    *,
    fixed_mins: list[int] | None = None,
) -> list[int]:
    """
    Build column widths: fixed prefix cols + N stat cols at full label width.
    Shrinks only the fixed prefix columns if the pane is narrow.
    """
    from cli.domain.stats import stat_column_width

    sw = stat_column_width()
    inner = _border_inner_max()
    n = len(fixed_widths) + stat_cols
    gaps = 2 * max(0, n - 1)
    need = sum(fixed_widths) + stat_cols * sw + gaps
    if need <= inner:
        out = list(fixed_widths)
    else:
        flex_budget = max(9, inner - gaps - stat_cols * sw)
        total = sum(fixed_widths) or 1
        out = [max(3, int(w * flex_budget / total)) for w in fixed_widths]
    if fixed_mins:
        for i, m in enumerate(fixed_mins):
            if i < len(out):
                out[i] = max(out[i], m)
    return out + [sw] * stat_cols


def _border_inner_max() -> int:
    return max(24, pane_content_width() - 6)
