from __future__ import annotations

from core.game_logic.player.player_model import PlayerModel
from core.game_logic.player.player_skill_collection_model import PlayerSkillModel
from core.game_logic.shared_game_config import SharedGameConfig
from core.game_logic.skill_builder import get_skill_damage_count
from core.game_logic.skill_description import (
    _has_damage_level,
    _has_health_level,
    _sum_active_damage_health,
)
from core.game_logic.player.player_item_stats import get_total_stats
from stat_display_format import format_ui_stat


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
