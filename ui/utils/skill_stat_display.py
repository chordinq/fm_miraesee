from __future__ import annotations

from core.game_logic.enums import StatNature, StatType
from core.game_logic.player.player_item_stats import get_total_stats
from core.game_logic.player.player_model import PlayerModel
from core.game_logic.player.player_skill_collection_model import PlayerSkillModel
from core.game_logic.shared_game_config import SharedGameConfig
from core.game_logic.skill_builder import get_skill_damage_count
from core.game_logic.skill_description import (
    _has_damage_level,
    _has_health_level,
    _sum_active_damage_health,
)
from ui.utils.stat_display_format import format_ui_stat

_BASE_LABEL_LOC_ID = "2060633843101697"
_BASE_LABEL_LOC_TABLE = "Skills"
_DAMAGE_LABEL_LOC_ID = "988835206590464"
_HEALTH_LABEL_LOC_ID = "989213239209984"
_STATS_LOC_TABLE = "Stats"


def format_skill_description_args(
    player: PlayerModel,
    skill: PlayerSkillModel,
    *,
    include_duration: bool = True,
) -> list[str]:
    game_config = player.game_config
    combat_skill = skill.type
    level = skill.level
    skill_config = game_config.skill_library.get(combat_skill)
    if skill_config is None:
        return []

    resolved = SharedGameConfig.get_resolved_active_skill_stats(
        game_config,
        combat_skill,
        level,
        get_total_stats(player),
    )
    damage, health = _sum_active_damage_health(resolved)
    args: list[str] = []

    if _has_damage_level(skill_config, level) and damage > 0:
        hit_count = get_skill_damage_count(combat_skill)
        per_hit = damage / hit_count
        args.append(format_ui_stat(per_hit))

    if _has_health_level(skill_config, level) and health > 0:
        args.append(format_ui_stat(health))

    if include_duration:
        duration = float(skill_config.get("ActiveDuration", 0.0))
        if duration > 0:
            args.append(format_ui_stat(duration))

    return args


def _format_positive_ui_stat(value: float) -> str:
    text = format_ui_stat(value)
    if not text.startswith(("+", "-")):
        return f"+{text}"
    return text


def _passive_label_segments(stat_type: StatType) -> list[dict[str, str]] | None:
    if stat_type == StatType.Damage:
        stat_loc_id = _DAMAGE_LABEL_LOC_ID
    elif stat_type == StatType.Health:
        stat_loc_id = _HEALTH_LABEL_LOC_ID
    else:
        return None
    return [
        {"locId": _BASE_LABEL_LOC_ID, "locTable": _BASE_LABEL_LOC_TABLE},
        {"locId": stat_loc_id, "locTable": _STATS_LOC_TABLE},
    ]


def _sum_passive_damage_health(resolved) -> tuple[float, float]:
    damage = 0.0
    health = 0.0
    for node, value in resolved.all_stat_contributions.items():
        if node.unique_stat.stat_nature != StatNature.Additive:
            continue
        if node.unique_stat.stat_type == StatType.Damage:
            damage += value
        elif node.unique_stat.stat_type == StatType.Health:
            health += value
    return damage, health


def _build_passive_line_segments(
    value: float,
    stat_type: StatType,
) -> list[dict[str, object]] | None:
    label_segments = _passive_label_segments(stat_type)
    if label_segments is None:
        return None

    segments: list[dict[str, object]] = [
        {"text": _format_positive_ui_stat(value)},
    ]
    for label in label_segments:
        segments.append(
            {
                "locId": label["locId"],
                "locTable": label["locTable"],
            }
        )
    return segments


def _with_trailing_spaces(
    segments: list[dict[str, object]],
) -> list[dict[str, object]]:
    if not segments:
        return segments
    result: list[dict[str, object]] = []
    for index, segment in enumerate(segments):
        entry = dict(segment)
        if index < len(segments) - 1:
            entry["suffix"] = " "
        result.append(entry)
    return result


def build_skill_passive_stat_segments(
    player: PlayerModel,
    skill: PlayerSkillModel,
) -> list[dict[str, object]]:
    resolved = SharedGameConfig.get_resolved_passive_skill_stats(
        player.game_config,
        skill.type,
        skill.level,
        get_total_stats(player),
    )
    damage, health = _sum_passive_damage_health(resolved)

    segments: list[dict[str, object]] = []
    for stat_type, value in ((StatType.Damage, damage), (StatType.Health, health)):
        if value <= 0:
            continue
        line_segments = _build_passive_line_segments(value, stat_type)
        if line_segments is None:
            continue
        segments.extend(line_segments)
    return _with_trailing_spaces(segments)
