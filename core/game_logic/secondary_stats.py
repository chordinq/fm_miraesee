from __future__ import annotations
from typing import Tuple
from ..miraesee_extension import miraesee_extension
from .enums import SecondaryStatType
from config import SECONDARY_STAT_LIBRARY

class SecondaryStats:
	def __init__(self) -> None:
		self.interpolated_stat_values: dict[SecondaryStatType, float] = {}

	def add_or_replace_stat_contribution(self, stat_type: SecondaryStatType, value: float) -> None:
		self.interpolated_stat_values[stat_type] = value

	def try_get_stat_value(self, stat_type: SecondaryStatType) -> Tuple[bool, float]:
		if stat_type not in self.interpolated_stat_values:
			return False, 0.0

		clamped_value = max(0.0, min(1.0, self.interpolated_stat_values[stat_type]))
		stat_name = stat_type.name
		stat_config = SECONDARY_STAT_LIBRARY.get(stat_name)

		lower_range = stat_config.get("LowerRange", 0.0)
		upper_range = stat_config.get("UpperRange", 0.0)
			
		return True, lower_range + (upper_range - lower_range) * clamped_value

	@property
	@miraesee_extension
	def perfection(self) -> float:
		return sum(self.interpolated_stat_values.values()) / len(self.interpolated_stat_values) if self.interpolated_stat_values else 0.0
