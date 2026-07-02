"""IL: SkillsLocalizer + GameContextExtensions.FormatSkillDescription."""
from __future__ import annotations

from core.game_logic.enums import CombatSkill, Rarity, StatNature, StatType
from core.game_logic.player.player_model import PlayerModel, get_total_stats
from core.game_logic.player.player_skill_collection_model import (
	PlayerSkillModel,
	get_skill_damage_count,
)
from core.game_logic.config.shared_game_config import SharedGameConfig

from .localizer import format_bracketed_entity_title
from .localizer_base import get_translation
from .number_format import format_stat

_SKILL_DESC_SUFFIX = "Desc"


def get_skill_name(skill: CombatSkill, *, language: str | None = None) -> str:
	"""IL: SkillsLocalizer.GetSkillName."""
	return get_translation(skill.name, table="Skills", language=language)


def get_skill_description_template(skill: CombatSkill, *, language: str | None = None) -> str:
	"""IL: SkillsLocalizer.GetSkillDescription — enum + ``Desc`` (template only)."""
	loc_key = f"{skill.name}{_SKILL_DESC_SUFFIX}"
	return get_translation(loc_key, table="Skills", language=language)


def get_skill_display_name(
	skill: CombatSkill,
	rarity: Rarity,
	*,
	language: str | None = None,
) -> str:
	"""IL: GameContextExtensions.GetSkillName."""
	return format_bracketed_entity_title(
		rarity,
		get_skill_name(skill, language=language),
		language=language,
	)


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


def _format_description_stat_arg(value: float) -> str:
	"""IL: NumberFormat.FormatStat for skill description placeholders."""
	return format_stat(value)


def _format_description_duration_arg(duration: float) -> str:
	"""IL: raw F64 passed to String.Format (not NumberFormat.FormatStat)."""
	if duration == int(duration):
		return str(int(duration))
	return f"{duration:g}"


def _skill_show_duration_in_description(skill_config: dict) -> bool:
	"""IL: SkillVisualDetails.ShowDuration (+0x18 on visual entry)."""
	if "ShowDuration" in skill_config:
		return bool(skill_config["ShowDuration"])
	return float(skill_config.get("ActiveDuration", 0.0)) > 0.0


def format_skill_description_args(
	player: PlayerModel,
	skill: PlayerSkillModel,
) -> list[str]:
	"""IL: GameContextExtensions.FormatSkillDescription — argument list only."""
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
		args.append(_format_description_stat_arg(per_hit))

	if _has_health_level(skill_config, level) and health > 0:
		args.append(_format_description_stat_arg(health))

	if _skill_show_duration_in_description(skill_config):
		duration = float(skill_config.get("ActiveDuration", 0.0))
		if duration > 0:
			args.append(_format_description_duration_arg(duration))

	return args


def format_skill_description(
	player: PlayerModel,
	skill: PlayerSkillModel,
) -> str:
	"""IL: FormatSkillDescription + SkillsLocalizer.GetSkillDescription + String.Format."""
	template = get_skill_description_template(skill.type)
	args = format_skill_description_args(player, skill)
	if not template:
		return ""
	if not args:
		return template
	try:
		return template.format(*args)
	except (IndexError, ValueError):
		return template


_BASE_PASSIVE_LABEL_KEY = "Base"
_DAMAGE_LABEL_KEY = "Damage"
_HEALTH_LABEL_KEY = "Health"
_STATS_LOC_TABLE = "Stats"
_SKILLS_LOC_TABLE = "Skills"


def _format_positive_stat(value: float) -> str:
	text = format_stat(value)
	if not text.startswith(("+", "-")):
		return f"+{text}"
	return text


def _sum_passive_damage_health(resolved) -> tuple[float, float]:
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


def format_skill_passive_stat_text(
	player: PlayerModel,
	skill: PlayerSkillModel,
	*,
	language: str | None = None,
) -> str:
	"""IL: passive pill — value + localized base/stat labels."""
	resolved = SharedGameConfig.get_resolved_passive_skill_stats(
		player.game_config,
		skill.type,
		skill.level,
		get_total_stats(player),
	)
	damage, health = _sum_passive_damage_health(resolved)

	parts: list[str] = []
	for stat_type, value in ((StatType.Damage, damage), (StatType.Health, health)):
		if value <= 0:
			continue
		stat_key = _DAMAGE_LABEL_KEY if stat_type == StatType.Damage else _HEALTH_LABEL_KEY
		base_label = get_translation(
			_BASE_PASSIVE_LABEL_KEY,
			table=_SKILLS_LOC_TABLE,
			language=language,
		)
		stat_label = get_translation(stat_key, table=_STATS_LOC_TABLE, language=language)
		parts.append(f"{_format_positive_stat(value)} {base_label} {stat_label}")

	return " ".join(parts)
