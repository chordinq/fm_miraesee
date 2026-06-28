from __future__ import annotations

from typing import TYPE_CHECKING, Mapping

from ...miraesee_extension import miraesee_extension
from ..enums import SecondaryStatType
from ..f64_math import f64_from_raw, f64_lerp_raw_from_t_raw, f64_to_raw

if TYPE_CHECKING:
	from ..shared_game_config import SharedGameConfig


class SecondaryStats:
	def __init__(
		self,
		interpolated_stat_values: Mapping[SecondaryStatType, int] | None = None,
	) -> None:
		self.interpolated_stat_values: dict[SecondaryStatType, int] = (
			dict(interpolated_stat_values) if interpolated_stat_values is not None else {}
		)

	def add_or_replace_stat_contribution(
		self,
		stat_type: SecondaryStatType,
		interpolation_value: float | int,
	) -> None:
		if isinstance(interpolation_value, int):
			raw = interpolation_value
		else:
			raw = f64_to_raw(interpolation_value)
		self.interpolated_stat_values[stat_type] = raw

	def try_get_stat_value(
		self,
		stat_type: SecondaryStatType,
		game_config: SharedGameConfig,
	) -> tuple[bool, float]:
		"""IL: SecondaryStats.TryGetStatValue → F64 lerp(LowerRange, UpperRange, Clamp01(t))."""
		if stat_type not in self.interpolated_stat_values:
			return False, 0.0

		row = game_config.secondary_stat_library.get(stat_type)
		if row is None:
			return False, 0.0

		t_raw = self.interpolated_stat_values[stat_type]
		lower = float(row["LowerRange"])
		upper = float(row["UpperRange"])
		result_raw = f64_lerp_raw_from_t_raw(lower, upper, t_raw)
		return True, f64_from_raw(result_raw)

	@property
	@miraesee_extension
	def perfection(self) -> float:
		if not self.interpolated_stat_values:
			return 0.0
		return sum(
			f64_from_raw(raw) for raw in self.interpolated_stat_values.values()
		) / len(self.interpolated_stat_values)
