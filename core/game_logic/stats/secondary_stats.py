from __future__ import annotations

from typing import TYPE_CHECKING, Mapping

from ...miraesee_extension import miraesee_extension
from ..enums import SecondaryStatType

if TYPE_CHECKING:
	from ..shared_game_config import SharedGameConfig


class SecondaryStats:
	def __init__(
		self,
		interpolated_stat_values: Mapping[SecondaryStatType, float] | None = None,
	) -> None:
		self.interpolated_stat_values: dict[SecondaryStatType, float] = (
			dict(interpolated_stat_values) if interpolated_stat_values is not None else {}
		)

	def add_or_replace_stat_contribution(
		self,
		stat_type: SecondaryStatType,
		interpolation_value: float,
	) -> None:
		self.interpolated_stat_values[stat_type] = float(interpolation_value)

	def try_get_stat_value(
		self,
		stat_type: SecondaryStatType,
		game_config: SharedGameConfig,
	) -> tuple[bool, float]:
		if stat_type not in self.interpolated_stat_values:
			return False, 0.0

		row = game_config.secondary_stat_library.get(stat_type)
		if row is None:
			return False, 0.0

		t = max(0.0, min(1.0, self.interpolated_stat_values[stat_type]))
		lower = float(row["LowerRange"])
		upper = float(row["UpperRange"])
		return True, lower + (upper - lower) * t

	@property
	@miraesee_extension
	def perfection(self) -> float:
		if not self.interpolated_stat_values:
			return 0.0
		return sum(self.interpolated_stat_values.values()) / len(
			self.interpolated_stat_values
		)
