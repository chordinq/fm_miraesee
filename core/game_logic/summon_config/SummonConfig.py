# core/game_logic/summon_config/SummonConfig.py
"""
Game.Logic.SummonConfig

Loaded once from a SummonConfig JSON at startup (via configs/config.py).
All simulators receive a SummonConfig instance rather than a raw dict.
"""

from __future__ import annotations

from core.enums import AscendableType, CurrencyType
from core.game_logic.summon_config.SummonLevelConfig import SummonLevelConfig


class SummonConfig:
	"""
	Game.Logic.SummonConfig : GameConfigKeyValue<SummonConfig>

	C# fields:
	  0x10  SummonableId              Id
	  0x18  Price                     SingleSummonCost
	  0x20  List<SummonLevelConfig>   Levels
	  0x28  List<int>                 PossibleSummonCount
	  0x30  int                       BulkSummonUnlockThreshold
	"""

	def __init__(self, data: dict) -> None:
		self.id:                         str | None        = data.get("Id")
		self._cost:                      dict              = data.get("SingleSummonCost", {})
		self.levels:                     list[SummonLevelConfig] = [
			SummonLevelConfig(lv) for lv in data.get("Levels", [])
		]
		self.possible_summon_count:      list[int]         = data.get("PossibleSummonCount", [])
		self.bulk_summon_unlock_threshold: int             = data.get("BulkSummonUnlockThreshold", 0)

	# ------------------------------------------------------------------
	# Cost helpers
	# ------------------------------------------------------------------

	@property
	def currency_type(self) -> CurrencyType:
		return CurrencyType[self._cost["Currency"]]

	@property
	def cost_per_summon(self) -> int:
		return int(self._cost["Amount"])

	# ------------------------------------------------------------------
	# SummonConfig$$CanAffordSummon / SummonConfig$$CanUnlockBulkSummons
	# ------------------------------------------------------------------

	def can_afford(self, player, count: int) -> bool:
		"""SummonConfig$$CanAffordSummon."""
		return player.get_currency(self.currency_type) >= self.cost_per_summon * count

	def can_unlock_bulk(self, player) -> bool:
		"""SummonConfig$$CanUnlockBulkSummons."""
		return player.get_currency(self.currency_type) >= self.bulk_summon_unlock_threshold

	def spend(self, player, count: int) -> None:
		"""Deduct the cost of [count] summons from player currency."""
		player.sub_currency(self.currency_type, self.cost_per_summon * count)

	# ------------------------------------------------------------------
	# Level config access
	# ------------------------------------------------------------------

	def get_level_config(self, level: int) -> SummonLevelConfig:
		"""SummonConfig$$get_Levels[level] with bounds clamping."""
		idx = min(max(level, 0), len(self.levels) - 1)
		return self.levels[idx]

	# ------------------------------------------------------------------
	# Progress / seed advancement  (called once per pull)
	# ------------------------------------------------------------------

	def advance_progress(self, summon_model) -> None:
		"""
		Increment summon count; roll level-up when SummonsRequired is reached.
		Uses the level BEFORE this pull to determine the threshold.
		"""
		level_cfg = self.get_level_config(summon_model.level)
		summon_model.count += 1
		if summon_model.count >= level_cfg.summons_required:
			summon_model.count -= level_cfg.summons_required
			summon_model.level += 1

	@staticmethod
	def advance_seed(summon_model) -> None:
		"""Increment the summon RNG seed by 1 after each pull."""
		summon_model.set_seed(summon_model.get_seed() + 1)
