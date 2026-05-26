from __future__ import annotations

from collections import defaultdict

from configs import STAT_DISPLAY_NAMES
from cli.domain.stats import stat_value
from cli.theme import BOLD, C_MUTED, C_WHITE, RESET, perf_color


def render(session) -> list[str]:
    records: list[tuple[str, float]] = []
    for skill in session.player.skills.skills.values():
        ss = getattr(skill, "secondary_stats", None)
        if ss:
            for s in ss.stats:
                records.append((s.stat_type.name, s.perfection))
    for pet in session.player.pets.pets:
        ss = getattr(pet, "secondary_stats", None)
        if ss:
            for s in ss.stats:
                records.append((s.stat_type.name, s.perfection))
    for mount in session.player.mounts.mounts:
        ss = getattr(mount, "secondary_stats", None)
        if ss:
            for s in ss.stats:
                records.append((s.stat_type.name, s.perfection))

    lines = [f"  {BOLD}COLLECTION STATS{RESET}", f"  {C_MUTED}{'─' * 48}{RESET}", ""]
    if not records:
        lines.append(f"  {C_MUTED}No stats.{RESET}")
        return lines

    grouped: dict[str, list[float]] = defaultdict(list)
    for n, p in records:
        grouped[n].append(p)

    for sname, perfs in sorted(grouped.items(), key=lambda kv: -len(kv[1])):
        disp = STAT_DISPLAY_NAMES.get(sname, sname)
        avg = sum(perfs) / len(perfs) * 100
        best = stat_value(sname, max(perfs))
        lines.append(
            f"  {C_WHITE}{disp:<22}{RESET}  {len(perfs):>4}  "
            f"{perf_color(avg)}{avg:>6.1f}%{RESET}  {best:>+7.2f}%"
        )
    return lines
