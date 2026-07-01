from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ..config.summon_config import SummonConfig

_MASK64 = 0xFFFFFFFFFFFFFFFF


class SummonModel:
	def __init__(
		self,
		count: int = 0,
		level: int = 0,
		seed: int = 0,
		can_bulk_summon: bool = False,
	) -> None:
		self.count = count
		self.level = level
		self.can_bulk_summon = can_bulk_summon
		self.seed = seed

	@property
	def seed(self) -> int:
		return self._seed

	@seed.setter
	def seed(self, new_seed: int) -> None:
		self._seed = new_seed & _MASK64

	def reset(self) -> None:
		self.count = 0
		self.level = 0

	def increment_summon_count(self, summon_config: SummonConfig) -> None:
		self.count += 1
		self.seed = (self._seed + 1) & _MASK64

		next_level_idx = self.level + 1
		if next_level_idx < len(summon_config.levels):
			next_level_cfg = summon_config.levels[next_level_idx]
			if next_level_cfg.summons_required <= self.count:
				self.count -= next_level_cfg.summons_required
				self.level += 1

	def try_unlock_bulk_summon(self, threshold: int) -> None:
		if not self.can_bulk_summon and self.count >= threshold:
			self.can_bulk_summon = True


def is_summon_level_maxed(summon_model: SummonModel, summon_config: SummonConfig) -> bool:
	"""IL: PlayerPropertyId*SummonLevelMaxed — level >= maxLevel - 1."""
	max_level = len(summon_config.levels)
	if max_level < 1:
		return False
	return summon_model.level >= max_level - 1
