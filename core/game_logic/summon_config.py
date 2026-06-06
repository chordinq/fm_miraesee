#updated 2026-06-03
from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from config import EGG_SUMMON_CONFIG, MOUNT_SUMMON_CONFIG, SKILL_SUMMON_CONFIG

from .enums import AscendableType, CurrencyType
from .player.player_currency_model import Price
from .stats.stat_target import (
	ActiveSkillStatTarget,
	EggStatTarget,
	MountStatTarget,
	StatTargetBase,
)
from .summon_level_config import SummonLevelConfig

if TYPE_CHECKING:
	from .player.player_model import PlayerModel
	from .player.player_currency_model import SpendContext

_ASCENDABLE_SUMMON_CONFIG: dict[AscendableType, dict] = {
	AscendableType.Skills: SKILL_SUMMON_CONFIG,
	AscendableType.Pets: EGG_SUMMON_CONFIG,
	AscendableType.Mounts: MOUNT_SUMMON_CONFIG,
}


class SummonableId:
	def __init__(self, id: str) -> None:
		self.id = id
	
	def get_stat_target(self) -> StatTargetBase:
		if self.id == "Skills":
			return ActiveSkillStatTarget()
		elif self.id == "Eggs":
			return EggStatTarget()
		elif self.id == "Mounts":
			return MountStatTarget()
		else:
			raise ValueError(f"Invalid summonable id: {self.id}")


class SummonConfig:
	def __init__(self, ascendable_type: AscendableType) -> None:
		try:
			data = _ASCENDABLE_SUMMON_CONFIG[ascendable_type]
		except KeyError:
			raise ValueError(
				f"SummonConfig requires Skills, Pets, or Mounts AscendableType, got {ascendable_type!r}"
			) from None

		single_summon_cost = data.get("SingleSummonCost")
		cost_amount = single_summon_cost["Amount"]
		cost_currency = CurrencyType[single_summon_cost["Currency"]]

		self.summonable_id: SummonableId = SummonableId(data.get("Id"))
		self.single_summon_cost: Price = Price(amount=cost_amount, currency=cost_currency)
		self.levels: list[SummonLevelConfig] = [SummonLevelConfig(lv) for lv in data.get("Levels")]
		self.possible_summon_count: list[int] = data.get("PossibleSummonCount")
		self.bulk_summon_unlock_threshold: int = data.get("BulkSummonUnlockThreshold")
	
	def get_base_summon_count(self) -> int:
		return self.possible_summon_count[0]

	def can_afford_summon(
		self,
		player_model: PlayerModel,
		summon_count: int,
	) -> tuple[bool, Optional[SpendContext]]:
		if player_model.player_currency_model.can_afford_price(self.single_summon_cost * summon_count):
			return True, player_model.player_currency_model.create_spend_context(self.single_summon_cost.currency, self.single_summon_cost.amount * summon_count)
		return False, None

	def min_summon_cycle_cost(self, player_model: PlayerModel) -> int:
		raise NotImplementedError("After implementing the currency model, implement this method")

	def max_summons_count(self, player_model: PlayerModel) -> int:
		raise NotImplementedError("After implementing the currency model, implement this method")
