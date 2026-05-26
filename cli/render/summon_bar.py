# cli/render/summon_bar.py — summon progress + ascension display (fixed columns)
from __future__ import annotations

from core.enums import AscensionLevel
from cli.core.ansi import pad_vis
from cli.theme import BOLD, C_GOLD, C_MUTED, C_WHITE, DIM, RESET

_BAR_W = 12
_LABEL_W = 8   # FORGE / SKILL / PET/EGG / MOUNT
_LV_W = 6      # Lv.999


def summon_progress_bar(count: int, required: int, width: int = _BAR_W) -> str:
    req = max(1, required)
    filled = min(width, int(width * count / req))
    empty = width - filled
    fill = f"{C_WHITE}{'█' * filled}{RESET}" if filled else ""
    ghost = f"{DIM}{'░' * empty}{RESET}" if empty else ""
    return fill + ghost


def format_ascension(level: int) -> str:
    if level <= 0:
        return ""
    try:
        a = AscensionLevel(level)
    except ValueError:
        return ""
    if a == AscensionLevel.None_:
        return ""
    tier = int(a)
    stars = f"{C_GOLD}★{RESET}" * tier + f"{C_MUTED}☆{RESET}" * (3 - tier)
    labels = {1: "Mega", 2: "Ultra", 3: "Apex"}
    return f"{stars} {labels.get(tier, '')}"


def format_profile_header(
    label: str,
    *,
    level: int,
    count: int | None = None,
    required: int | None = None,
    ascension_level: int = 0,
) -> str:
    """Aligned header: label | Lv | [bar | count/required | ascension]."""
    label_part = pad_vis(f"{BOLD}{label}{RESET}", _LABEL_W)
    lv_part = pad_vis(f"Lv.{C_WHITE}{level + 1}{RESET}", _LV_W)
    if count is None or required is None:
        return f"  {label_part}  {lv_part}"
    bar = summon_progress_bar(count, required)
    frac = pad_vis(f"{C_MUTED}{count}/{required}{RESET}", 8)
    asc = format_ascension(ascension_level)
    tail = f"  {asc}" if asc else ""
    return f"  {label_part}  {lv_part}  {bar}  {frac}{tail}"


def format_summon_header(
    label: str,
    *,
    level: int,
    count: int,
    required: int,
    ascension_level: int,
) -> str:
    return format_profile_header(
        label,
        level=level,
        count=count,
        required=required,
        ascension_level=ascension_level,
    )
