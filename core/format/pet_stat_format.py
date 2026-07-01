from __future__ import annotations

from typing import Any

from core.game_logic.player.player_pet_collection_model import PetId
from core.game_logic.config.shared_game_config import SharedGameConfig
from core.game_logic.stats.stats import Stats

from .item_stat_format import format_secondary_stats_collection
from .stats_format import format_stat_node


def format_pet_stats(
	game_config: SharedGameConfig,
	pet_id: PetId,
	secondary_stats: Any,
	level: int,
	total_stats: Stats,
	*,
	show_secondary_stats: bool = True,
) -> str:
	"""IL: SharedGameConfigExtensions.FormatPetStats (display — not Game.Logic namespace)."""
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
