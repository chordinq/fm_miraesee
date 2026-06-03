"""
ONLY FOR REFERENCE — disabled until game_logic APIs are migrated.
Re-enable by uncommenting the block below.
"""

# from __future__ import annotations
#
# from config import MOUNT_LIBRARY, MOUNTS_MAPPING, SECONDARY_STAT_PET_UNLOCK
# from core.enums import Rarity, SummonKind, TechTreeNodeType
# from core.random_pcg import RandomPCG
# from core.game_logic.player_model import MountModel, PlayerModel
# from core.game_logic.summon_config import SummonConfig
# from core.game_logic.summon_cost import can_afford_summon_batch, spend_summon_batch
# from core.game_logic.stat_helper import StatHelper
# from core.game_logic.stat_helper import SecondaryStatHelper
# from .summon_base import SummonPullResult, SummonResult
#
#
# def _build_mounts_by_rarity() -> dict[str, list[str]]:
# 	pools: dict[str, list[str]] = {r.name: [] for r in Rarity}
# 	for key, data in sorted(MOUNT_LIBRARY.items(), key=lambda kv: kv[1]["MountId"]["Id"]):
# 		pools[data["MountId"]["Rarity"]].append(key)
# 	return pools
#
#
# _MOUNTS_BY_RARITY: dict[str, list[str]] = _build_mounts_by_rarity()
# _MOUNT_ID_CACHE:   dict[str, int]        = {k: v["MountId"]["Id"] for k, v in MOUNT_LIBRARY.items()}
#
# _PET_STAT_COUNT: dict[str, int] = {
# 	k: v["NumberOfSecondStats"] for k, v in SECONDARY_STAT_PET_UNLOCK.items()
# }
#
#
# class MountSummonSimulator:
# 	def __init__(self, player: PlayerModel, config: SummonConfig) -> None:
# 		self.player = player
# 		self.config = config
#
# 	def summon(self, count: int) -> SummonResult:
# 		config       = self.config
# 		summon_model = self.player.mounts.summon_model
#
# 		if count not in config.possible_summon_count:
# 			return SummonResult(SummonKind.Mounts, count, 0, success=False, error="invalid_summon_count")
#
# 		if not can_afford_summon_batch(
# 			self.player, config, TechTreeNodeType.MountSummonCost, count
# 		):
# 			return SummonResult(SummonKind.Mounts, count, 0, success=False, error="insufficient_currency")
#
# 		spend_summon_batch(self.player, config, TechTreeNodeType.MountSummonCost, count)
# 		pulls: list[SummonPullResult] = []
# 		total_target = count
# 		pull_idx     = 0
#
# 		while pull_idx < total_target:
# 			is_bonus = pull_idx >= count
# 			seed     = summon_model.get_seed()
# 			rng      = RandomPCG(seed)
#
# 			if not is_bonus and StatHelper.roll_bonus_summon(self.player, SummonKind.Mounts, rng):
# 				total_target += 1
#
# 			level_cfg = config.get_level_config(summon_model.level)
# 			rarity    = level_cfg.roll_rarity(rng)
#
# 			pool      = _MOUNTS_BY_RARITY[rarity.name]
# 			mount_key = pool[rng.next_int(len(pool))]
#
# 			rng.next_guid()
#
# 			stat_count = _PET_STAT_COUNT.get(rarity.name, 1)
# 			secondary  = SecondaryStatHelper.generate_secondary_stats(stat_count, rng)
#
# 			mount_id = _MOUNT_ID_CACHE[mount_key]
# 			mount    = MountModel(mount_id, rarity)
# 			mount.secondary_stats = secondary
#
# 			owned  = {m.mount_id for m in self.player.mounts.mounts if m.rarity == rarity}
# 			is_new = mount_id not in owned
# 			self.player.mounts.add_mount(mount)
#
# 			name = next(
# 				(d["Key"] for d in MOUNTS_MAPPING.values() if d.get("Idx") == mount_id and d.get("Rarity") == rarity.value),
# 				str(mount_id),
# 			)
# 			pulls.append(SummonPullResult(
# 				rarity, is_new, name.replace(" ", ""),
# 				is_bonus=is_bonus, secondary_stats=secondary,
# 			))
#
# 			config.advance_progress(summon_model)
# 			config.advance_seed(summon_model)
# 			pull_idx += 1
#
# 		return SummonResult(SummonKind.Mounts, count, len(pulls), pulls=pulls)
