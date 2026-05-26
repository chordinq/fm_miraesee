# cli/domain/stats.py — stat formatting & filters (no I/O)
from __future__ import annotations

from configs import STAT_RANGES, STAT_DISPLAY_NAMES

_NEGATIVE = {"SkillCooldownMulti"}
MIN_STAT_COLUMNS = 2
_STAT_VALUE_CHARS = len("+100.00%")


def stat_display_name_max_len() -> int:
    return max(len(v) for v in STAT_DISPLAY_NAMES.values())


def stat_column_width() -> int:
    """Column width for full stat label + value (e.g. 'Skill Cooldown +12.34%')."""
    return stat_display_name_max_len() + 1 + _STAT_VALUE_CHARS


def stat_value(stat_type_name: str, perfection: float) -> float:
    r = STAT_RANGES.get(stat_type_name, {})
    lo, hi = r.get("lower", 0.0), r.get("upper", 1.0)
    return (lo + (hi - lo) * perfection) * 100.0


def _sign(name: str) -> str:
    return "-" if name in _NEGATIVE else "+"


def fmt_stat_value_colored(stat_type_name: str, perfection: float) -> str:
    from cli.theme import RESET, perf_color
    val = stat_value(stat_type_name, perfection)
    return f"{perf_color(perfection * 100)}{_sign(stat_type_name)}{val:.2f}%{RESET}"


def stat_value_display_len(stat_type_name: str, perfection: float) -> float:
    val = stat_value(stat_type_name, perfection)
    return len(f"{_sign(stat_type_name)}{val:.2f}%")


def fmt_stat_hatch(stat_type_name: str, perfection: float, col_width: int = 0) -> str:
    if col_width > 0:
        return fmt_stat_table_cell(stat_type_name, perfection, col_width)
    name = STAT_DISPLAY_NAMES.get(stat_type_name, stat_type_name)
    val_part = fmt_stat_value_colored(stat_type_name, perfection)
    vlen = int(stat_value_display_len(stat_type_name, perfection))
    width = len(name) + 2 + vlen
    gap = max(2, width - len(name) - vlen)
    return name + (" " * gap) + val_part


def fmt_stat_table_cell(stat_type_name: str, perfection: float, col_width: int) -> str:
    """Stat column: label left, colored in-game value right-aligned in the cell."""
    name = STAT_DISPLAY_NAMES.get(stat_type_name, stat_type_name)
    val_part = fmt_stat_value_colored(stat_type_name, perfection)
    val_v = int(stat_value_display_len(stat_type_name, perfection))
    max_name = max(1, col_width - val_v - 1)
    if len(name) > max_name:
        name = name[:max_name]
    gap = max(1, col_width - len(name) - val_v)
    return name + (" " * gap) + val_part


def fmt_stat_table_empty(col_width: int) -> str:
    from cli.core.ansi import pad_vis
    from cli.theme import C_MUTED, RESET

    dash = f"{C_MUTED}-{RESET}"
    return pad_vis(dash, col_width, align="c")
