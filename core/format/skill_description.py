from __future__ import annotations

from core.game_logic.enums import StatNature, StatType
from core.game_logic.player.player_model import PlayerModel, get_total_stats
from core.game_logic.player.player_skill_collection_model import PlayerSkillModel
from core.game_logic.config.shared_game_config import SharedGameConfig
from core.game_logic.player.player_skill_collection_model import get_skill_damage_count

from .number_format import format_stat


def _sum_active_damage_health(resolved) -> tuple[float, float]:
	damage = 0.0
	health = 0.0
	for node, value in resolved.iter_stat_contributions_double():
		if node.unique_stat.stat_nature != StatNature.Additive:
			continue
		if node.unique_stat.stat_type == StatType.Damage:
			damage += value
		elif node.unique_stat.stat_type == StatType.Health:
			health += value
	return damage, health


def _has_damage_level(skill_config: dict, level: int) -> bool:
	damage_levels = skill_config.get("DamagePerLevel", [])
	return level < len(damage_levels) and bool(damage_levels[level])


def _has_health_level(skill_config: dict, level: int) -> bool:
	health_levels = skill_config.get("HealthPerLevel", [])
	return level < len(health_levels) and bool(health_levels[level])


def _format_description_arg(value: float) -> str:
	return format_stat(value)


def _append_duration_arg(
	args: list[str],
	skill_config: dict,
	include_duration: bool,
) -> None:
	if not include_duration:
		return
	duration = float(skill_config.get("ActiveDuration", 0.0))
	if duration <= 0:
		return
	args.append(_format_description_arg(duration))


def format_skill_description_args(
	player: PlayerModel,
	skill: PlayerSkillModel,
	*,
	include_duration: bool = True,
) -> list[str]:
	"""IL: GameContextExtensions.FormatSkillDescription"""
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
		args.append(_format_description_arg(per_hit))

	if _has_health_level(skill_config, level) and health > 0:
		args.append(_format_description_arg(health))

	_append_duration_arg(args, skill_config, include_duration)
	return args
