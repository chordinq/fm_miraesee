"""
ONLY FOR REFERENCE — disabled until game_logic APIs are migrated.
Re-enable by uncommenting the block below.
"""

# from __future__ import annotations
#
# from ..enums import SummonKind
# from ...random_pcg import RandomPCG
# from ..model import EggModel, PlayerModel
# from .pet_hatch import predict_hatch
# from ..summon_config import SummonConfig
# from ..stat_helper import StatHelper
# from .summon_base import SummonPullResult, SummonResult
#
#
# class EggSummonSimulator:
# 	def __init__(self, player: PlayerModel, config: SummonConfig) -> None:
# 		self.player = player
# 		self.config = config
#
# 	def summon(self, count: int) -> SummonResult:
# 		config       = self.config
# 		summon_model = self.player.pets.summon_model
#
# 		if count not in config.possible_summon_count:
# 			return SummonResult(SummonKind.Pets, count, 0, success=False, error="invalid_summon_count")
#
# 		config.spend(self.player, count)
# 		pulls: list[SummonPullResult] = []
# 		total_target = count
# 		pull_idx     = 0
#
# 		while pull_idx < total_target:
# 			is_bonus = pull_idx >= count
# 			seed     = summon_model.get_seed()
# 			rng      = RandomPCG(seed)
#
# 			if not is_bonus and StatHelper.roll_bonus_summon(self.player, SummonKind.Pets, rng):
# 				total_target += 1
#
# 			level_cfg = config.get_level_config(summon_model.level)
# 			rarity    = level_cfg.roll_rarity(rng)
#
# 			egg = EggModel(rarity, seed)
# 			self.player.pets.add_egg(egg)
#
# 			pred = predict_hatch(egg, self.player)
# 			pulls.append(SummonPullResult(
# 				rarity,
# 				True,
# 				pred.pet_name,
# 				is_bonus=is_bonus,
# 				secondary_stats=pred.secondary_stats,
# 				egg_seed=seed,
# 				pet_idx=pred.pet_idx,
# 			))
#
# 			config.advance_progress(summon_model)
# 			config.advance_seed(summon_model)
# 			pull_idx += 1
#
# 		return SummonResult(SummonKind.Pets, count, len(pulls), pulls=pulls)
