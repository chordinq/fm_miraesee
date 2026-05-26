from __future__ import annotations

from configs import ITEM_MAPPING
from cli.domain.display_names import display_name
from cli.domain.stats import stat_value
from cli.theme import BOLD, C_MUTED, RESET, age_color, perf_color


def render(result, count: int) -> list[str]:
    if not result.success:
        from cli.theme import err
        return [f"  {err(result.error)}"]

    pulls = result.pulls
    free = getattr(result, "free_forge_count", 0)
    note = f"  {C_MUTED}(+{free} free){RESET}" if free else ""
    lines = [f"  {BOLD}FORGE{RESET}  ×{count}{note}", f"  {C_MUTED}{'─' * 48}{RESET}", ""]
    for i, pull in enumerate(pulls, 1):
        key = f"{pull.age.value}_{pull.item_type.value}_{pull.idx}"
        data = ITEM_MAPPING.get(key, {})
        name = display_name(data.get("Name", pull.item_type.name))
        ac = age_color(pull.age.value)
        lines.append(f"  {C_MUTED}#{i:>3}{RESET}  {ac}{BOLD}{name}{RESET}  {pull.item_type.name}")
        for s in pull.secondary_stats.stats:
            from configs import STAT_DISPLAY_NAMES
            sn = STAT_DISPLAY_NAMES.get(s.stat_type.name, s.stat_type.name)
            v = stat_value(s.stat_type.name, s.perfection)
            lines.append(f"         {sn:<18}  {perf_color(s.perfection * 100)}{v:+.2f}%{RESET}")
        lines.append("")
    return lines
