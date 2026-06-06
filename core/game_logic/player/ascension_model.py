from __future__ import annotations
from typing import TYPE_CHECKING
from ..enums import AscendableType, AscensionLevel
from ..stats import StatContributions
from ..stats.stat_helper import StatHelper

if TYPE_CHECKING:
	from ..shared_game_config import SharedGameConfig


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
