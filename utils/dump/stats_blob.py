from __future__ import annotations

from core.game_logic.enums import SecondaryStatType
from core.game_logic.stats import SecondaryStats

from .schema import STATS_CHUNK_LEN


def parse_stats_blob(
	stats_blob: str,
	*,
	max_stats: int = 2,
) -> SecondaryStats:
	result = SecondaryStats()
	for s_idx in range(max_stats):
		start = s_idx * STATS_CHUNK_LEN
		chunk = stats_blob[start : start + STATS_CHUNK_LEN]
		if chunk == "0000000000" or len(chunk) < STATS_CHUNK_LEN:
			continue
		try:
			stat_type = SecondaryStatType(int(chunk[1], 16))
			raw_val = int(chunk[2:STATS_CHUNK_LEN], 16)
		except (ValueError, KeyError):
			continue
		if raw_val == 0:
			continue
		result.add_or_replace_stat_contribution(stat_type, raw_val)
	return result
