# core/game_logic/mount_summon.py
"""
Mount summon simulator.

Per pull (C# MountSummonFinalizedAction$$Execute + MountExtensions$$CreateMount):
  rng  = RandomPCG(seed)               CreateFromSeed(seed)
  StatHelper$$RollStat bonus check     NextFixedD6 (1 PCG call)
  rarity = SummonLevelConfig$$RollRarity(rng)
  mount_key = pool[rng.next_int(N)]    RandomPCG$$Choice -> list[NextInt(N)]  (1 PCG call)
  rng.next_guid()                      RandomPCGExtensions$$NextGuid -> 4 PCG calls
  stats = generate_secondary_stats(    SecondaryStatHelper$$GenerateSecondaryStats
      stat_count, rng)                   -> len(available_types) + 1 PCG calls per stat
  seed += 1
"""

from __future__ import annotations

from configs import MOUNT_LIBRARY, MOUNT_MAPPING, SECONDARY_STAT_PET_UNLOCK
from core.enums import Rarity, SummonKind
from core.enums import RARITY_NAMES
from core.random_pcg import RandomPCG
from core.game_logic.player_model.MountModel import MountModel
from core.game_logic.player_model.PlayerModel import PlayerModel
from core.game_logic.summon_config import SummonConfig
from core.game_logic.stat_helper import StatHelper
from core.game_logic.secondary_stats import generate_secondary_stats
from core.game_logic.summon_base import SummonPullResult, SummonResult


def _build_mounts_by_rarity() -> dict[str, list[str]]:
	pools: dict[str, list[str]] = {name: [] for name in RARITY_NAMES}
	for key, data in sorted(MOUNT_LIBRARY.items(), key=lambda kv: kv[1]["MountId"]["Id"]):
		pools[data["MountId"]["Rarity"]].append(key)
	return pools


_MOUNTS_BY_RARITY: dict[str, list[str]] = _build_mounts_by_rarity()
_MOUNT_ID_CACHE:   dict[str, int]        = {k: v["MountId"]["Id"] for k, v in MOUNT_LIBRARY.items()}

_PET_STAT_COUNT: dict[str, int] = {
	k: v["NumberOfSecondStats"] for k, v in SECONDARY_STAT_PET_UNLOCK.items()
}


class MountSummonSimulator:
	def __init__(self, player: PlayerModel, config: SummonConfig) -> None:
		self.player = player
		self.config = config

	def summon(self, count: int) -> SummonResult:
		config       = self.config
		summon_model = self.player.mounts.summon_model

		if count not in config.possible_summon_count:
			return SummonResult(SummonKind.Mounts, count, 0, success=False, error="invalid_summon_count")

		config.spend(self.player, count)
		pulls: list[SummonPullResult] = []
		total_target = count
		pull_idx     = 0

		while pull_idx < total_target:
			is_bonus = pull_idx >= count
			seed     = summon_model.get_seed()
			rng      = RandomPCG(seed)

			# PCG call #1: StatHelper$$RollStat (ExtraMountChance bonus check)
			if not is_bonus and StatHelper.roll_bonus_summon(self.player, SummonKind.Mounts, rng):
				total_target += 1

			# PCG call #2: SummonLevelConfig$$RollRarity
			level_cfg = config.get_level_config(summon_model.level)
			rarity    = level_cfg.roll_rarity(rng)

			# PCG call #3: RandomPCG$$Choice -> list[NextInt(count)]  (1 PCG call)
			pool      = _MOUNTS_BY_RARITY[rarity.name]
			mount_key = pool[rng.next_int(len(pool))]

			# PCG calls #4..#7: RandomPCGExtensions$$NextGuid (2 x NextULong)
			rng.next_guid()

			# PCG calls (7+N)..: SecondaryStatHelper$$GenerateSecondaryStats
			stat_count = _PET_STAT_COUNT.get(rarity.name, 1)
			secondary  = generate_secondary_stats(stat_count, rng)

			mount_id = _MOUNT_ID_CACHE[mount_key]
			mount    = MountModel(mount_id, rarity)
			mount.secondary_stats = secondary

			owned  = {m.mount_id for m in self.player.mounts.mounts if m.rarity == rarity}
			is_new = mount_id not in owned
			self.player.mounts.add_mount(mount)

			name = next(
				(d["Name"] for d in MOUNT_MAPPING.values() if d["idx"] == mount_id and d["Rarity"] == rarity.value),
				str(mount_id),
			)
			pulls.append(SummonPullResult(
				rarity, is_new, name.replace(" ", ""),
				is_bonus=is_bonus, secondary_stats=secondary,
			))

			config.advance_progress(summon_model)
			config.advance_seed(summon_model)
			pull_idx += 1

		return SummonResult(SummonKind.Mounts, count, len(pulls), pulls=pulls)
