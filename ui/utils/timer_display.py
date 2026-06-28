"""IL: TimeExtensions.Format(TimeSpan/MetaDuration, digits=2) — upgrade timer label text."""

from __future__ import annotations

import json

from localizer import LOCALIZATIONS_DIR

_DAYS_D_LOC_ID = "28308895591755776"
_HOURS_H_LOC_ID = "28308895591755777"
_MINUTES_M_LOC_ID = "28307134017630208"
_SECONDS_S_LOC_ID = "28307134051184640"
_DEFAULT_LANGUAGE = "en"


def _load_loc_string(loc_id: str, table: str, language: str) -> str:
    path = LOCALIZATIONS_DIR / f"{table}_{language}.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        for entry in data["m_TableData"]:
            if str(entry["m_Id"]) == loc_id:
                return entry["m_Localized"]
    except (OSError, KeyError, json.JSONDecodeError, TypeError):
        pass
    return ""


def _timer_units(language: str) -> tuple[str, str, str, str]:
    return (
        _load_loc_string(_DAYS_D_LOC_ID, "General", language) or "d",
        _load_loc_string(_HOURS_H_LOC_ID, "General", language) or "h",
        _load_loc_string(_MINUTES_M_LOC_ID, "General", language) or "m",
        _load_loc_string(_SECONDS_S_LOC_ID, "General", language) or "s",
    )


def format_timer_duration(
    seconds: int,
    language: str = _DEFAULT_LANGUAGE,
    *,
    digits: int = 2,
) -> str:
    """IL: TimeExtensions.Format — up to `digits` largest non-zero d/h/m/s components."""
    if digits <= 0:
        return ""

    total_seconds = max(0, int(seconds))
    days = total_seconds // 86400
    remainder = total_seconds % 86400
    hours = remainder // 3600
    remainder %= 3600
    minutes = remainder // 60
    secs = remainder % 60

    day_unit, hour_unit, minute_unit, second_unit = _timer_units(language)
    parts: list[str] = []
    count = 0

    if days >= 1:
        parts.append(f"{days}{day_unit}")
        count += 1

    if hours > 0 and count < digits:
        parts.append(f"{hours}{hour_unit}")
        count += 1

    if minutes > 0 and count < digits:
        parts.append(f"{minutes}{minute_unit}")
        count += 1

    if secs >= 1 and count < digits:
        parts.append(f"{secs}{second_unit}")

    return " ".join(parts)


def format_hatch_duration(seconds: int, language: str = _DEFAULT_LANGUAGE) -> str:
    return format_timer_duration(seconds, language)
