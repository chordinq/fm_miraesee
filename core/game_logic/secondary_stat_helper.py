from __future__ import annotations

from typing import Sequence

from .enums import SecondaryStatType
from .random_pcg import RandomPCG
from .secondary_stats import SecondaryStats

_stat_ranges_cache: dict[str, dict[str, float]] | None = None


class SecondaryStatHelper:
	"""Game.Logic.SecondaryStatHelper — rolled secondary stats (perfection → range)."""

	@staticmethod
	def stat_ranges() -> dict[str, dict[str, float]]:
		global _stat_ranges_cache
		if _stat_ranges_cache is None:
			from config import SECONDARY_STAT_LIBRARY

			_stat_ranges_cache = {
				name: {
					"lower": float(data["LowerRange"]),
					"upper": float(data["UpperRange"]),
				}
				for name, data in SECONDARY_STAT_LIBRARY.items()
			}
		return _stat_ranges_cache

	@staticmethod
	def stat_pool() -> list[str]:
		return list(SecondaryStatHelper.stat_ranges().keys())

	@staticmethod
	def display_name(stat_type_name: str) -> str:
		from config import STATS_MAPPING

		for entry in STATS_MAPPING.get("SecondaryStatType", {}).values():
			if entry.get("Key") == stat_type_name:
				return entry["Key"]
		return stat_type_name

	@staticmethod
	def stat_value(stat_type: SecondaryStatType, perfection: float) -> float:
		if not perfection:
			return 0.0
		ranges = SecondaryStatHelper.stat_ranges().get(stat_type.name)
		if not ranges:
			return 0.0
		return ranges["lower"] + (perfection * (ranges["upper"] - ranges["lower"]))

	@staticmethod
	def generate_secondary_stats(
		stat_count: int,
		rng: RandomPCG,
		excluded_types: Sequence[SecondaryStatType] | None = None,
	) -> SecondaryStats:
		available = list(SecondaryStatType)
		if excluded_types:
			for stat_type in excluded_types:
				try:
					available.remove(stat_type)
				except ValueError:
					pass

		result = SecondaryStats()
		while stat_count > 0:
			if not available:
				break
			stat_type = rng.choice(available)
			perfection = rng.next_f64()
			result.add_or_replace_stat_contribution(stat_type, perfection)
			available.remove(stat_type)
			stat_count -= 1
		return result
