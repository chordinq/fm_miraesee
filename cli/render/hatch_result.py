# cli/render/hatch_result.py — ID / Name / Type / Stat1 / Stat2
from __future__ import annotations

from cli.domain.display_names import display_name
from cli.domain.registries.egg_ids import egg_id_from_seed, egg_id_suffix
from cli.domain.stats import fmt_stat_table_cell, fmt_stat_table_empty
from cli.render.align import table_cols_with_stats
from cli.render.data_table import render_table
from cli.render.summon.split_view import _pet_type
from cli.theme import BOLD, C_MUTED, RESET, rarity_color

_TYPE_COL_W = len("Balanced")


def _stat_cell(stats, idx: int, col_width: int) -> str:
    if not stats or idx >= len(stats.stats):
        return fmt_stat_table_empty(col_width)
    s = stats.stats[idx]
    return fmt_stat_table_cell(s.stat_type.name, s.perfection, col_width)


def render(preds: list) -> list[str]:
    if not preds:
        return [f"  {BOLD}HATCH{RESET}", "", f"  {C_MUTED}(no eggs){RESET}"]

    col_w = table_cols_with_stats(
        [3, 14, _TYPE_COL_W],
        stat_cols=2,
        fixed_mins=[3, 12, _TYPE_COL_W],
    )
    stat_w = col_w[-1]

    headers = ["ID", "Name", "Type", "Stat1", "Stat2"]
    rows = []
    for pr in preds:
        rc = rarity_color(pr.rarity.value)
        eid = egg_id_suffix(egg_id_from_seed(pr.egg_seed))
        rows.append([
            f"{C_MUTED}{eid}{RESET}",
            f"{rc}{BOLD}{display_name(pr.pet_name)}{RESET}",
            _pet_type(pr.rarity.value, pr.pet_idx),
            _stat_cell(pr.secondary_stats, 0, stat_w),
            _stat_cell(pr.secondary_stats, 1, stat_w),
        ])

    lines = [
        f"  {BOLD}HATCH{RESET}  {C_MUTED}×{len(preds)}{RESET}",
        "",
    ]
    lines.extend(
        render_table(
            headers,
            rows,
            col_w=col_w,
            header_align="c",
            col_align=["c", "c", "c", "l", "l"],
        )
    )
    return lines
