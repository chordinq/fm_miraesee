# cli/render/summon/split_view.py — Result grid + Detailed (egg/mount only)
from __future__ import annotations

from configs import STAT_DISPLAY_NAMES, PET_MAPPING, SKILL_MAPPING, MOUNT_MAPPING
from cli.domain.display_names import display_name
from cli.domain.registries.egg_ids import egg_id_from_seed
from cli.domain.stats import fmt_stat_table_cell, fmt_stat_table_empty, stat_value
from cli.render.align import collection_column_widths, grid_row_5, pane_content_width, table_cols_with_stats
from cli.render.collection_grid import rounded_box
from cli.render.data_table import render_table
from cli.render.split_pane import hub_pane_width
from cli.theme import BOLD, C_MUTED, RESET, perf_color, rarity_color

_SKILL_GROUP = 5
_DASH = f"{C_MUTED}-{RESET}"


def _skill_name(detail: str) -> str:
    c = detail.replace(" ", "")
    for d in SKILL_MAPPING.values():
        n = d.get("Name", "")
        if n.replace(" ", "") == c:
            return display_name(n)
    return display_name(detail)


def _mount_name(detail: str) -> str:
    c = detail.replace(" ", "")
    for d in MOUNT_MAPPING.values():
        n = d.get("Name", "")
        if n.replace(" ", "") == c:
            return display_name(n)
    return display_name(detail)


def _egg_name(pull) -> str:
    if pull.pet_idx is not None:
        key = f"{pull.rarity.value}_{pull.pet_idx}"
        return display_name(PET_MAPPING.get(key, {}).get("Name", pull.detail))
    return display_name(pull.detail)


def _pet_type(rv: int, idx: int) -> str:
    from core.enums import PetBalancingType
    raw = PET_MAPPING.get(f"{rv}_{idx}", {}).get("Type", 0)
    try:
        bt = PetBalancingType(raw)
        cols = {
            "Damage": "\033[38;2;231;76;60m",
            "Health": "\033[38;2;46;204;113m",
            "Balanced": "\033[38;2;52;152;219m",
        }
        c = cols.get(bt.name, "")
        return f"{c}{bt.name}{RESET}"
    except (ValueError, KeyError):
        return "?"


def _stat_cell(stats, idx: int, col_width: int = 0) -> str:
    if col_width <= 0:
        if not stats or idx >= len(stats.stats):
            return _DASH
        s = stats.stats[idx]
        key = s.stat_type.name
        label = STAT_DISPLAY_NAMES.get(key, key)
        v = stat_value(key, s.perfection)
        return f"{label} {perf_color(s.perfection * 100)}{v:+.2f}%{RESET}"
    if not stats or idx >= len(stats.stats):
        return fmt_stat_table_empty(col_width)
    s = stats.stats[idx]
    return fmt_stat_table_cell(s.stat_type.name, s.perfection, col_width)


def _pull_number(kind: str, index: int) -> int:
    if kind == "skill":
        return (index // _SKILL_GROUP) + 1
    return index + 1


def _result_rows(pulls: list, name_fn) -> list[str]:
    """5-column result grid inside a rounded box (matches Collection style)."""
    items = []
    for p in pulls:
        rc = rarity_color(p.rarity.value)
        nm = name_fn(p)
        star = f"{C_MUTED}*{RESET}" if p.is_bonus else ""
        items.append(f"{rc}{nm}{RESET}{star}")

    col_widths = collection_column_widths(_SKILL_GROUP, 1)
    inner_w = sum(col_widths) + (_SKILL_GROUP - 1) * 1

    if not items:
        return rounded_box([f"{C_MUTED}(none){RESET}"], max(inner_w, 12))

    body: list[str] = []
    for i in range(0, len(items), _SKILL_GROUP):
        body.append(grid_row_5(items[i : i + _SKILL_GROUP], col_widths))
    return rounded_box(body, inner_w)


def _detailed_egg(pulls: list) -> list[str]:
    from cli.domain.registries.egg_ids import egg_id_suffix

    type_w = len("Balanced")
    col_w = table_cols_with_stats(
        [3, 3, 14, type_w],
        stat_cols=2,
        fixed_mins=[3, 3, 12, type_w],
    )
    stat_w = col_w[-1]
    headers = ["#", "ID", "Name", "Type", "Stat1", "Stat2"]
    rows = []
    for i, p in enumerate(pulls):
        num = _pull_number("egg", i)
        rc = rarity_color(p.rarity.value)
        raw = egg_id_from_seed(p.egg_seed) if p.egg_seed is not None else "?"
        eid = egg_id_suffix(raw) if raw != "?" else "?"
        idx = p.pet_idx or 0
        rows.append([
            f"{C_MUTED}{num}{RESET}",
            f"{C_MUTED}{eid}{RESET}",
            f"{rc}{BOLD}{_egg_name(p)}{RESET}",
            _pet_type(p.rarity.value, idx),
            _stat_cell(p.secondary_stats, 0, stat_w),
            _stat_cell(p.secondary_stats, 1, stat_w),
        ])
    return render_table(
        headers,
        rows,
        col_w=col_w,
        header_align="c",
        col_align=["c", "c", "c", "c", "l", "l"],
    )


def _detailed_mount(pulls: list) -> list[str]:
    headers = ["#", "Name", "Stat1", "Stat2"]
    col_w = table_cols_with_stats([3, 14], stat_cols=2)
    stat_w = col_w[-1]
    rows = []
    for i, p in enumerate(pulls):
        num = _pull_number("mount", i)
        rc = rarity_color(p.rarity.value)
        rows.append([
            f"{C_MUTED}{num}{RESET}",
            f"{rc}{BOLD}{_mount_name(p.detail)}{RESET}",
            _stat_cell(p.secondary_stats, 0, stat_w),
            _stat_cell(p.secondary_stats, 1, stat_w),
        ])
    return render_table(
        headers,
        rows,
        col_w=col_w,
        header_align="c",
        col_align=["c", "c", "l", "l"],
    )


def render_split(
    title: str,
    pulls: list,
    kind: str,
    count: int,
) -> list[str]:
    pane = hub_pane_width()
    bonus = sum(1 for p in pulls if getattr(p, "is_bonus", False))
    note = f"  {C_MUTED}(+{bonus} bonus){RESET}" if bonus else ""

    name_fn = {
        "skill": lambda p: _skill_name(p.detail),
        "egg": _egg_name,
        "mount": lambda p: _mount_name(p.detail),
    }[kind]
    result = _result_rows(pulls, name_fn)

    lines = [
        f"  {BOLD}{title}{RESET}  ×{count}{note}",
        f"  {C_MUTED}{'─' * min(pane_content_width(), 48)}{RESET}",
        "",
        f"  {BOLD}Result{RESET}",
        "",
    ]
    lines.extend(result)

    if kind == "skill":
        return lines

    div = f"  {C_MUTED}{'─' * min(pane_content_width(), 60)}{RESET}"
    detail = _detailed_egg(pulls) if kind == "egg" else _detailed_mount(pulls)
    lines += ["", div, f"  {BOLD}Detailed{RESET}", ""]
    lines.extend(detail)
    return lines
