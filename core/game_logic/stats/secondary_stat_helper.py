from __future__ import annotations
from typing import TYPE_CHECKING, Sequence
from ..enums import SecondaryStatType
from ...random_pcg import RandomPCG
from .secondary_stats import SecondaryStats

if TYPE_CHECKING:
	from ..shared_game_config import SharedGameConfig


class SecondaryStatHelper:
	@staticmethod
	def inverse_lerp(value: float, lower: float, upper: float) -> float:
		span = upper - lower
		if span == 0.0:
			return 0.0
		return (value - lower) / span

	@staticmethod
	def get_interpolated_value_from_calculated_value(
		stat_type: SecondaryStatType,
		calculated_value: float,
		game_config: SharedGameConfig,
	) -> float:
		row = game_config.secondary_stat_library.get(stat_type)
		if row is None:
			raise ValueError(f"Missing SecondaryStatLibrary entry: {stat_type!r}")
		lower = float(row["LowerRange"])
		upper = float(row["UpperRange"])
		return SecondaryStatHelper.inverse_lerp(calculated_value, lower, upper)

	@staticmethod
	def generate_secondary_stats(
		stat_count: int,
		random: RandomPCG,
		excluded_types: Sequence[SecondaryStatType] | None = None,
	) -> SecondaryStats:
		available = list(SecondaryStatType)
		if excluded_types:
			excluded = set(excluded_types)
			available = [t for t in available if t not in excluded]

		result = SecondaryStats()
		remaining = stat_count
		while remaining > 0:
			if not available:
				break
			stat_type = random.choice(available)
			interpolation = random.next_f64()
			result.add_or_replace_stat_contribution(stat_type, interpolation)
			available.remove(stat_type)
			remaining -= 1
		return result
