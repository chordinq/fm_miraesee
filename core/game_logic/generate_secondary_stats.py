from __future__ import annotations

from typing import Sequence

from .enums import SecondaryStatType
from .random_pcg import RandomPCG
from .player_model import SecondaryStatsModel, StatModel

def generate_secondary_stats(
	stat_count: int,
	rng: RandomPCG,
	excluded_types: Sequence[SecondaryStatType] | None = None,
) -> SecondaryStatsModel:
	
	available: list[SecondaryStatType] = list(SecondaryStatType)
	if excluded_types:
		for t in excluded_types:
			try:
				available.remove(t)
			except ValueError:
				pass

	result = SecondaryStatsModel()
	for _ in range(stat_count):
		if not available:
			break
		idx = rng.next_int(len(available))
		stat_type: SecondaryStatType = available.pop(idx)
		perfection: float = rng.next_f64()
		result.add_stat(StatModel(stat_type, perfection))

	return result
