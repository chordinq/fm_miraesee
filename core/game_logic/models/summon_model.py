from ..enums import SummonKind
from ..summon_config import SummonConfig

class SummonModel:
	def __init__(
		self,
		count: int = 0,
		level: int = 0,
		seed: int = 0,
		can_bulk_summon: bool = False
	) -> None:
		self.count = count
		self.level = level
		self.can_bulk_summon = can_bulk_summon
		self.seed = seed

	@property
	def seed(self) -> int:
		return self._seed

	@seed.setter
	def seed(self, new_seed: int):
		self._seed = new_seed & 0xFFFFFFFFFFFFFFFF

	def increment_summon_count(self, summon_config: SummonConfig) -> None:
		raise NotImplementedError("Not implemented")
