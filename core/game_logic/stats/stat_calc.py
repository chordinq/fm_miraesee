from __future__ import annotations
from dataclasses import dataclass
from ..enums import StatCondition, StatNature
from core.metaplaymath.fd6 import fd6_add_raw


@dataclass
class StatCalcContext:
	is_ranged: bool | None = None

	def is_condition_met(self, condition: StatCondition) -> bool:
		if condition == StatCondition.None_:
			return True
		if self.is_ranged is None:
			return False
		if condition == StatCondition.Melee:
			return not self.is_ranged
		if condition == StatCondition.Ranged:
			return self.is_ranged
		return False


@dataclass
class LayerBucket:
	additive: int = 0
	multiplier: int = 0
	divisor: int = 0
	one_minus_multiplier: int = 0
	has_multiplier: bool = False
	has_divisor: bool = False

	@classmethod
	def create(cls) -> LayerBucket:
		return cls()

	def add(self, nature: StatNature, value_raw: int) -> None:
		if nature == StatNature.Multiplier:
			self.multiplier = fd6_add_raw(self.multiplier, value_raw)
			self.has_multiplier = True
		elif nature == StatNature.Additive:
			self.additive = fd6_add_raw(self.additive, value_raw)
		elif nature == StatNature.Divisor:
			self.divisor = fd6_add_raw(self.divisor, value_raw)
			self.has_divisor = True
		elif nature == StatNature.OneMinusMultiplier:
			self.one_minus_multiplier = fd6_add_raw(self.one_minus_multiplier, value_raw)
