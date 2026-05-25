# core/game_logic/secondary_stats.py
"""
SecondaryStatHelper$$GenerateSecondaryStats

C# algorithm:
  1. Build available = list(SecondaryStatType)
  2. Remove any types already present (excluded_types param -- usually None)
  3. For i in range(stat_count):
       stat_type  = RandomPCG$$Choice(pcg, available)   -> len(available) PCG calls
       perfection = RandomPCG$$NextF64(pcg)              -> 1 PCG call
       result.add(stat_type, perfection)
       available.remove(stat_type)                       -> no duplicates
  4. Return SecondaryStats
"""

from __future__ import annotations

from typing import Sequence

from core.enums import SecondaryStatType
from core.game_logic.player_model.SecondaryStatsModel import SecondaryStatsModel
from core.game_logic.player_model.StatModel import StatModel
from core.random_pcg import RandomPCG


def generate_secondary_stats(
	stat_count: int,
	rng: RandomPCG,
	excluded_types: Sequence[SecondaryStatType] | None = None,
) -> SecondaryStatsModel:
	"""
	SecondaryStatHelper$$GenerateSecondaryStats(stat_count, pcg, excluded, 0).

	Args:
	    stat_count:     number of secondary stats to generate.
	    rng:            active RandomPCG -- consumed in-place.
	    excluded_types: stat types already present elsewhere (usually None).
	"""
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
		stat_type: SecondaryStatType = rng.choice(available)
		perfection: float = rng.next_f64()
		result.add_stat(StatModel(stat_type, perfection))
		available.remove(stat_type)

	return result
