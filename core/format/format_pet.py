"""IL: PetVisualConfig, SharedGameConfigExtensions.FormatPetStats*."""
from __future__ import annotations

from typing import Any

from core.game_logic.enums import Rarity
from core.game_logic.player.player_pet_collection_model import PetId, PlayerPetModel
from core.game_logic.config.shared_game_config import SharedGameConfig
from core.game_logic.stats.stats import Stats

from .format_item import format_secondary_stats_collection
from .localizer import format_bracketed_entity_title
from .localizer_base import get_translation
from .stats_format import format_stat_comparison_flat, format_stat_node


def get_pet_name(name_key: str, *, language: str | None = None) -> str:
	"""IL: PetVisualConfig.GetPetNameLocalized."""
	return get_translation(name_key, table="Pets", language=language)


def get_pet_display_name(
	name_key: str,
	rarity: Rarity,
	*,
	language: str | None = None,
) -> str:
	"""IL: GameContextExtensions.GetName(PetId)."""
	return format_bracketed_entity_title(
		rarity,
		get_pet_name(name_key, language=language),
		language=language,
	)


def format_pet_stats(
	game_config: SharedGameConfig,
	pet_id: PetId,
	secondary_stats: Any,
	level: int,
	total_stats: Stats,
	*,
	show_secondary_stats: bool = True,
) -> str:
	"""IL: SharedGameConfigExtensions.FormatPetStats."""
	lines: list[str] = []
	resolved = SharedGameConfig.get_resolved_pet_stats(
		game_config, pet_id, level, total_stats
	)
	for stat_node, fd6_value in resolved.iter_stat_contributions_double():
		text = format_stat_node(
			stat_node,
			fd6_value,
			show_multipliers_as_percentage=False,
			show_value_at_end=False,
		)
		if text:
			lines.append(text)
	if show_secondary_stats:
		secondary_text = format_secondary_stats_collection(secondary_stats, game_config)
		if secondary_text:
			lines.extend(secondary_text.split("\n"))
	return "\n".join(lines)


def format_pet_stats_upgrade_mode(
	game_config: SharedGameConfig,
	pet: PlayerPetModel,
	player_stats: Stats,
	level: int,
	target_level: int,
) -> str:
	"""IL: SharedGameConfigExtensions.FormatPetStatsUpgradeMode."""
	current = SharedGameConfig.get_resolved_pet_stats(
		game_config,
		pet.pet_id,
		level,
		player_stats,
	)
	target = SharedGameConfig.get_resolved_pet_stats(
		game_config,
		pet.pet_id,
		target_level,
		player_stats,
	)

	def _stat_key(stat_node) -> tuple:
		return (
			stat_node.unique_stat.stat_type,
			stat_node.unique_stat.stat_nature,
			stat_node.target.kind,
			stat_node.target.qualifiers,
			stat_node.condition,
		)

	target_values: dict[tuple, float] = {}
	for stat_node, value in target.iter_stat_contributions_double():
		target_values[_stat_key(stat_node)] = value

	lines: list[str] = []
	for stat_node, current_value in current.iter_stat_contributions_double():
		target_value = target_values.get(_stat_key(stat_node), 0.0)
		line = format_stat_comparison_flat(
			stat_node,
			current_value,
			target_value,
			show_multipliers_as_percentage=False,
		)
		if line:
			lines.append(line)
	return "\n".join(lines)
