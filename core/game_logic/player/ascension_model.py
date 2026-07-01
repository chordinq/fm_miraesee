from __future__ import annotations
from typing import TYPE_CHECKING
from ..enums import AscendableType, AscensionLevel, CurrencyType
from ..stats import StatContributions
from ..stats.stat_helper import StatHelper
from ..player.player_currency_model import Price

if TYPE_CHECKING:
	from ..config.shared_game_config import SharedGameConfig
	from .player_model import PlayerModel


class AscensionModel:
	def __init__(
		self,
		ascendable_type: AscendableType,
		current_level: int = AscensionLevel.None_.value,
	) -> None:
		self.ascendable_type = ascendable_type
		self.current_level = current_level

	def ascend(self) -> None:
		self.current_level += 1

	def descend(self) -> None:
		self.current_level = max(0, self.current_level - 1)

	def get_ascension_configs(self, game_config: SharedGameConfig) -> dict | None:
		return game_config.ascension_configs_library.get(self.ascendable_type)

	def is_maxed(self, game_config: SharedGameConfig) -> bool:
		configs = self.get_ascension_configs(game_config) or {}
		return self.current_level >= len(configs.get("AscensionConfigPerLevel", []))

	def get_level_stats(self, game_config: SharedGameConfig) -> StatContributions:
		result = StatContributions()
		if self.current_level == AscensionLevel.None_.value:
			return result

		configs = self.get_ascension_configs(game_config)
		if not configs:
			return result

		level_configs = configs.get("AscensionConfigPerLevel", [])
		index = self.current_level - 1
		if 0 <= index < len(level_configs):
			for row in level_configs[index].get("StatContributions", []):
				result.stats.append(StatHelper.parse_stat_contribution_row(row))
		return result


def get_ascension_model(
	ascendable_type: AscendableType,
	player: PlayerModel,
) -> AscensionModel:
	if ascendable_type == AscendableType.Forge:
		return player.player_forge_model.ascension_model
	if ascendable_type == AscendableType.Mounts:
		return player.player_mount_collection_model.ascension_model
	if ascendable_type == AscendableType.Pets:
		return player.player_pet_collection_model.ascension_model
	if ascendable_type == AscendableType.Skills:
		return player.player_skill_collection_model.ascension_model
	raise ValueError(f"Unknown AscendableType: {ascendable_type!r}")


def get_ascension_cost(
	ascension_model: AscensionModel,
	game_config: SharedGameConfig,
) -> Price:
	configs = ascension_model.get_ascension_configs(game_config)
	if configs is None:
		raise ValueError(
			f"Missing ascension config for {ascension_model.ascendable_type!r}"
		)

	level_configs = configs.get("AscensionConfigPerLevel", [])
	if ascension_model.current_level >= len(level_configs):
		raise ValueError(
			f"Ascension level {ascension_model.current_level} has no cost row"
		)

	cost_row = level_configs[ascension_model.current_level].get("Cost", {})
	currency_name = cost_row.get("Currency")
	if currency_name is None:
		raise ValueError("Ascension cost row missing Currency")
	return Price(
		int(cost_row.get("Amount", 0)),
		CurrencyType[currency_name] if isinstance(currency_name, str) else CurrencyType(int(currency_name)),
	)


def get_ascension_cost_for_type(
	ascendable_type: AscendableType,
	player: PlayerModel,
) -> Price:
	return get_ascension_cost(
		get_ascension_model(ascendable_type, player),
		player.game_config,
	)


def ascensions_maxed(ascendable_type: AscendableType, player: PlayerModel) -> bool:
	return get_ascension_model(ascendable_type, player).is_maxed(player.game_config)


def ascension_conditions_met(
	ascendable_type: AscendableType,
	player: PlayerModel,
) -> bool:
	return ascension_conditions_met_for_model(
		get_ascension_model(ascendable_type, player),
		player,
	)


def ascension_conditions_met_for_model(
	ascension_model: AscensionModel,
	player: PlayerModel,
) -> bool:
	"""IL: AscensionExtensions.AscensionConditionsMet(AscensionModel, PlayerModel)."""
	if ascension_model.is_maxed(player.game_config):
		return False

	from ..config.features import is_unlocked as is_feature_unlocked

	return is_feature_unlocked(ascension_model.ascendable_type, player)


def ascend_forge(player: PlayerModel) -> None:
	"""IL: AscensionExtensions.AscendForge."""
	player.player_forge_model.ascend(player)
	player.player_equipment_model.ascend()
	player.player_power_model.update_power(player, publish_update=True)


def ascend_mounts(player: PlayerModel) -> None:
	"""IL: AscensionExtensions.AscendMounts."""
	player.player_mount_collection_model.ascend()
	player.player_power_model.update_power(player, publish_update=True)


def ascend_pets(player: PlayerModel) -> None:
	"""IL: AscensionExtensions.AscendPets."""
	player.player_pet_collection_model.ascend()
	player.player_power_model.update_power(player, publish_update=True)


def ascend_skills(player: PlayerModel) -> None:
	"""IL: AscensionExtensions.AscendSkills."""
	player.player_skill_collection_model.ascend()
	player.player_power_model.update_power(player, publish_update=True)


def ascend(ascendable_type: AscendableType, player: PlayerModel) -> None:
	"""IL: AscensionExtensions.Ascend."""
	match ascendable_type:
		case AscendableType.Forge:
			ascend_forge(player)
		case AscendableType.Mounts:
			ascend_mounts(player)
		case AscendableType.Pets:
			ascend_pets(player)
		case AscendableType.Skills:
			ascend_skills(player)
		case _:
			raise ValueError(f"Ascend: unknown type {ascendable_type!r}")
