from __future__ import annotations

from core.game_logic.player.player_techtree_model import _stat_value_at_level
from config import TECH_TREE_LIBRARY
from core.game_logic.enums import StatNature, TechTreeNodeType
from core.game_logic.player.player_model import PlayerModel
from core.game_logic.config.shared_game_config import SharedGameConfig
from core.game_logic.stats.stat_helper import StatHelper
from core.game_logic.stats.stat_target import DungeonStatTarget
from ui.utils.stat_display_format import (
    format_ui_dungeon_percent,
    format_ui_percentage,
    format_ui_stat,
)
from ui.utils.timer_display import format_timer_duration

_TIER_ROMAN = ("I", "II", "III", "IV", "V")


def _tier_addition_value(lib_entry: dict, tier: int) -> float:
    tier_additions = lib_entry.get("TierAddition") or []
    if tier < 0 or tier >= len(tier_additions):
        return 0.0
    return float(tier_additions[tier])


def _format_tech_tree_stat_value(stat_node, value: float) -> str:
    nature = stat_node.unique_stat.stat_nature
    if nature == StatNature.Additive:
        return format_ui_stat(value)

    if isinstance(stat_node.stat_target, DungeonStatTarget):
        return format_ui_dungeon_percent(value)

    if nature == StatNature.Multiplier:
        return format_ui_percentage(value, positive=True)
    if nature == StatNature.OneMinusMultiplier:
        return format_ui_percentage(value, positive=False)
    if nature == StatNature.Divisor:
        return format_ui_percentage(value, positive=True)

    return format_ui_stat(value, as_multiplier=True)


def tier_roman_numeral(tier: int) -> str:
    if 0 <= tier < len(_TIER_ROMAN):
        return _TIER_ROMAN[tier]
    return ""


def lookup_upgrade_level_info(
    game_config: SharedGameConfig,
    tier: int,
    internal_level: int,
) -> tuple[int, int] | None:
    lib_entry = game_config.tech_tree_upgrade_library.get(tier)
    if lib_entry is None:
        return None
    for row in lib_entry.get("Levels") or []:
        if int(row.get("Level", -1)) == internal_level:
            return int(row.get("Cost", 0)), int(float(row.get("Duration", 0.0)))
    return None


def format_upgrade_duration(seconds: int, language: str = "en") -> str:
    return format_timer_duration(seconds, language)


def build_tech_tree_per_level_increase(
    node_type: int,
    tier: int,
) -> str:
    try:
        node_enum = TechTreeNodeType(node_type)
    except ValueError:
        return ""

    lib_entry = TECH_TREE_LIBRARY.get(node_enum.name)
    if lib_entry is None:
        return ""

    stats = lib_entry.get("Stats") or []
    if not stats:
        return ""

    row = stats[0]
    value_increase = float(row.get("ValueIncrease", 0.0))
    stat_node = StatHelper.parse_stat_node(row["StatNode"])
    formatted = _format_tech_tree_stat_value(stat_node, value_increase)
    if not formatted:
        return ""
    if formatted.startswith(("+", "-")):
        return f"({formatted})"
    return f"(+{formatted})"


def build_tech_tree_desc_format_args(
    node_type: int,
    tier: int,
    ui_level: int,
) -> list[str]:
    try:
        node_enum = TechTreeNodeType(node_type)
    except ValueError:
        return []

    lib_entry = TECH_TREE_LIBRARY.get(node_enum.name)
    if lib_entry is None:
        return []

    stats = lib_entry.get("Stats") or []
    if not stats:
        return []

    internal_level = max(0, ui_level - 1)
    tier_bonus = _tier_addition_value(lib_entry, tier)
    row = stats[0]
    value = _stat_value_at_level(row, internal_level, tier_bonus)
    stat_node = StatHelper.parse_stat_node(row["StatNode"])
    return [_format_tech_tree_stat_value(stat_node, value)]
