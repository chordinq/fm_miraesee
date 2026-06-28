from __future__ import annotations

from config import STATS_MAPPING
from core.game_logic.enums import SecondaryStatType, StatType
from core.game_logic.player.player_item_stats import get_total_stats
from core.game_logic.player.player_model import PlayerModel
from core.game_logic.player.player_pet_collection_model import PlayerPetModel
from core.game_logic.shared_game_config import SharedGameConfig

_DAMAGE_LABEL_LOC_ID = "988835206590464"
_HEALTH_LABEL_LOC_ID = "989213239209984"
_STATS_LOC_TABLE = "Stats"


def _label_loc_segments(localizations: list[dict]) -> list[dict[str, str]]:
	return [
		{"locId": str(loc["Id"]), "locTable": loc["File"]}
		for loc in localizations
	]


def _secondary_label_segments(stat_type: SecondaryStatType) -> list[dict[str, str]]:
	entry = STATS_MAPPING["SecondaryStatType"][str(int(stat_type.value))]
	return _label_loc_segments(entry["Localization"])


def _primary_label_segments(stat_type: StatType) -> list[dict[str, str]] | None:
	if stat_type == StatType.Damage:
		return [{"locId": _DAMAGE_LABEL_LOC_ID, "locTable": _STATS_LOC_TABLE}]
	if stat_type == StatType.Health:
		return [{"locId": _HEALTH_LABEL_LOC_ID, "locTable": _STATS_LOC_TABLE}]
	return None


def build_pet_stat_lines(
	player: PlayerModel,
	pet: PlayerPetModel,
) -> list[dict[str, object]]:
	"""IL: PetDetailsUiView.UpdateUi → Config.FormatPetStats (split for QML labels)."""
	game_config = player.game_config
	total_stats = get_total_stats(player)
	resolved = SharedGameConfig.get_resolved_pet_stats(
		game_config,
		pet.pet_id,
		pet.level,
		total_stats,
	)

	lines: list[dict[str, object]] = []
	for stat_node, raw_value in resolved.all_stat_contributions.items():
		label_segments = _primary_label_segments(stat_node.unique_stat.stat_type)
		if label_segments is None:
			continue
		lines.append(
			{
				"rawValue": raw_value,
				"secondaryStatType": -1,
				"labelLocSegments": label_segments,
				"secondary": False,
			}
		)

	if pet.secondary_stats.interpolated_stat_values:
		for stat_type in pet.secondary_stats.interpolated_stat_values.keys():
			found, raw_value = pet.secondary_stats.try_get_stat_value(stat_type, game_config)
			if not found:
				continue
			lines.append(
				{
					"rawValue": raw_value,
					"secondaryStatType": int(stat_type.value),
					"labelLocSegments": _secondary_label_segments(stat_type),
					"secondary": True,
				}
			)

	return lines
