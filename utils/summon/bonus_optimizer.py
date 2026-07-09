"""Freebie-bonus path optimizer for Egg and Mount summons.

Algorithm
---------
Given ``start_seed``, ``chance_raw`` (FD6 freebie threshold), a list of
allowed batch sizes, and a total base-pull budget, find the exact sequence of
batch sizes that maximises the number of freebie (bonus) pulls.

Key observations that keep this tractable without pruning:

1. Each pull at global offset *g* uses a fresh ``RandomPCG.create_from_seed(start_seed + g)``.
   Whether it fires a freebie depends only on the seed and ``chance_raw`` — fixed for
   the duration of an optimisation run.

2. The DP state is ``(remaining_budget, seed_offset)``.  For a batch of size N
   starting at offset *o*:
   - Count freebies B = sum(freebie[o .. o+N-1])
   - Advance to state (remaining-N, o+N+B)
   Bonus pulls consume seeds but generate no further freebies.

3. Pre-compute the freebie bool array and a prefix-sum table so each batch
   evaluation is O(1).

4. The DP stores ``(best bonus count, fewest batch presses)`` per (rem, offset) cell.
   When bonus counts tie, prefer the path with fewer summon button presses (more
   bulk batches such as 50 / 15 rather than repeated 1-pulls).
   A separate parent table enables O(budget) path reconstruction after the
   search ends — no list copying inside the main loop.

State-space bound: max offset ≤ total_budget * (1 + max_freebie_rate), which
is O(budget) in practice.  Total cells = O(budget²) — e.g. ~10 000 for a
budget of 100, ~90 000 for 300.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from core.game_logic.enums import StatNature, StatType
from core.game_logic.stats.stat_helper import StatHelper
from core.game_logic.stats.stat_target import EggStatTarget, MountStatTarget
from core.random_pcg import RandomPCG

if TYPE_CHECKING:
	from core.game_logic.game_logic import GameLogic

__all__ = [
	"BonusOptimizationResult",
	"optimize_egg_summon_bonus",
	"optimize_mount_summon_bonus",
]

_FREEBIE_OVERSCAN = 4


@dataclass(frozen=True)
class BonusOptimizationResult:
	total_budget: int
	best_bonus_count: int
	best_total_pulls: int
	best_path: list[int] = field(default_factory=list)
	route_segments: list[str] = field(default_factory=list)
	route_str: str = ""


def _path_to_segments(path: list[int]) -> list[str]:
	if not path:
		return []
	segments: list[str] = []
	curr = path[0]
	cnt = 1
	for batch_n in path[1:]:
		if batch_n == curr:
			cnt += 1
		else:
			segments.append(f"{curr}x{cnt}")
			curr = batch_n
			cnt = 1
	segments.append(f"{curr}x{cnt}")
	return segments


def _compress_path(path: list[int]) -> str:
	segments = _path_to_segments(path)
	if not segments:
		return "(empty)"
	return " → ".join(segments)


def _is_better_bonus_path(
	new_bonus: int,
	new_batch_count: int,
	prev_bonus: int,
	prev_batch_count: int,
) -> bool:
	if new_bonus > prev_bonus:
		return True
	if new_bonus == prev_bonus and new_batch_count < prev_batch_count:
		return True
	return False


def _optimize_bonus_core(
	start_seed: int,
	chance_raw: int,
	possible_summon_counts: list[int],
	total_budget: int,
) -> BonusOptimizationResult:
	if total_budget <= 0:
		return BonusOptimizationResult(
			total_budget=0,
			best_bonus_count=0,
			best_total_pulls=0,
		)

	max_batch = max(possible_summon_counts)

	# Upper-bound on seed offset: every pull fires a freebie → offset ≤ 2*budget.
	# Add one extra batch worth of look-ahead to cover the last transition safely.
	precompute_len = total_budget * 2 + max_batch + _FREEBIE_OVERSCAN

	# Bool array: freebie_fires[g] = True if seed (start_seed+g) fires freebie as base pull
	freebie: list[bool] = [
		RandomPCG.create_from_seed(start_seed + g).compare_fixed_d6_less_than(chance_raw)
		for g in range(precompute_len)
	]

	# Prefix sum for O(1) range freebie counts
	prefix: list[int] = [0] * (precompute_len + 1)
	for i, f in enumerate(freebie):
		prefix[i + 1] = prefix[i] + (1 if f else 0)

	def count_freebies(offset: int, length: int) -> int:
		end = offset + length
		if end > precompute_len:
			return prefix[precompute_len] - prefix[offset]
		return prefix[end] - prefix[offset]

	# DP: dp[rem][offset] = (best bonus count, fewest batches) from this state
	# Use plain dicts; missing entries are unvisited.
	dp: list[dict[int, tuple[int, int]]] = [{} for _ in range(total_budget + 1)]
	# parent[(rem, offset)] = (prev_rem, prev_offset, batch_n)
	parent: dict[tuple[int, int], tuple[int, int, int]] = {}

	dp[total_budget][0] = (0, 0)

	for rem in range(total_budget, 0, -1):
		for offset, (bonus_so_far, batches_so_far) in dp[rem].items():
			for batch_n in possible_summon_counts:
				if batch_n > rem:
					continue
				b = count_freebies(offset, batch_n)
				new_offset = offset + batch_n + b
				new_rem = rem - batch_n
				new_bonus = bonus_so_far + b
				new_batch_count = batches_so_far + 1

				prev_entry = dp[new_rem].get(new_offset)
				if prev_entry is None:
					should_update = True
				else:
					prev_bonus, prev_batch_count = prev_entry
					should_update = _is_better_bonus_path(
						new_bonus,
						new_batch_count,
						prev_bonus,
						prev_batch_count,
					)
				if should_update:
					dp[new_rem][new_offset] = (new_bonus, new_batch_count)
					parent[(new_rem, new_offset)] = (rem, offset, batch_n)

	# Find best terminal state at rem=0
	best_bonus = -1
	best_batch_count = 0
	best_offset = 0
	for offset, (bonus, batch_count) in dp[0].items():
		if _is_better_bonus_path(bonus, batch_count, best_bonus, best_batch_count):
			best_bonus = bonus
			best_batch_count = batch_count
			best_offset = offset

	if best_bonus < 0:
		return BonusOptimizationResult(
			total_budget=total_budget,
			best_bonus_count=0,
			best_total_pulls=total_budget,
		)

	# Reconstruct path via parent table
	path: list[int] = []
	rem, offset = 0, best_offset
	while rem < total_budget:
		prev_rem, prev_offset, batch_n = parent[(rem, offset)]
		path.append(batch_n)
		rem, offset = prev_rem, prev_offset
	path.reverse()

	best_total = total_budget + best_bonus

	segments = _path_to_segments(path)

	return BonusOptimizationResult(
		total_budget=total_budget,
		best_bonus_count=best_bonus,
		best_total_pulls=best_total,
		best_path=path,
		route_segments=segments,
		route_str=_compress_path(path),
	)


def optimize_egg_summon_bonus(
	logic: GameLogic,
	total_budget: int,
) -> BonusOptimizationResult:
	"""Find the egg-summon batch sequence that maximises freebie pulls.

	Args:
		logic: Live ``GameLogic`` — player state is read but never mutated.
		total_budget: Total number of *base* pulls to distribute across batches.

	Returns:
		:class:`BonusOptimizationResult` with the optimal path and bonus count.
	"""
	player = logic.player
	summon_config = player.game_config.egg_summon_config
	summon_model = player.player_pet_collection_model.summon_model

	target = EggStatTarget()
	stats = StatHelper._player_total_stats(player)
	game_config = StatHelper._player_game_config(player)
	chance_raw = stats.get_stat_value_or_default_fd6_raw(
		game_config, StatType.FreebieChance, StatNature.Multiplier, target
	)

	return _optimize_bonus_core(
		start_seed=summon_model.seed,
		chance_raw=chance_raw,
		possible_summon_counts=list(summon_config.possible_summon_count),
		total_budget=total_budget,
	)


def optimize_mount_summon_bonus(
	logic: GameLogic,
	total_budget: int,
) -> BonusOptimizationResult:
	"""Find the mount-summon batch sequence that maximises freebie pulls.

	Args:
		logic: Live ``GameLogic`` — player state is read but never mutated.
		total_budget: Total number of *base* pulls to distribute across batches.

	Returns:
		:class:`BonusOptimizationResult` with the optimal path and bonus count.
	"""
	player = logic.player
	summon_config = player.game_config.mount_summon_config
	summon_model = player.player_mount_collection_model.summon_model

	target = MountStatTarget()
	stats = StatHelper._player_total_stats(player)
	game_config = StatHelper._player_game_config(player)
	chance_raw = stats.get_stat_value_or_default_fd6_raw(
		game_config, StatType.FreebieChance, StatNature.Multiplier, target
	)

	return _optimize_bonus_core(
		start_seed=summon_model.seed,
		chance_raw=chance_raw,
		possible_summon_counts=list(summon_config.possible_summon_count),
		total_budget=total_budget,
	)
