# ui/services/display_level.py — dump-stored level → UI level (+1)
from __future__ import annotations

from ui.theme.config.loc_ids import LV_PREFIX_LOC_ID
from ui.services.localization import translate_id


def display_level(dump_level: int) -> int:
    """In-game dump stores level - 1; UI shows dump + 1."""
    return int(dump_level) + 1


def format_level(dump_level: int) -> str:
    prefix = translate_id(LV_PREFIX_LOC_ID) or "Lv."
    return f"{prefix} {display_level(dump_level)}"
