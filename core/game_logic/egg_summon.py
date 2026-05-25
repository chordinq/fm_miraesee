# core/game_logic/egg_summon.py
"""
Egg (pet) summon simulator.

Per pull (C# EggSummonFinalizedAction$$Execute):
  rng  = RandomPCG(seed)               CreateFromSeed(seed)
  StatHelper$$RollStat bonus check     NextFixedD6 (1 PCG call)
  rarity = SummonLevelConfig$$RollRarity(rng)
  EggModel(rarity, seed)               CreateEggModel uses its OWN PCG for GUID;
                                         main rng is discarded here.
  seed += 1

Pet stats are NOT determined at summon time. CreateEggModel stores the original
seed, and the pet is created with stats when the egg is hatched.
"""

from __future__ import annotations

from configs import PET_MAPPING
from core.enums import SummonKind
from core.random_pcg import RandomPCG
from core.game_logic.player_model.EggModel import EggModel
from core.game_logic.player_model.PlayerModel import PlayerModel
from core.game_logic.summon_config import SummonConfig
from core.game_logic.stat_helper import StatHelper
from core.game_logic.summon_base import SummonPullResult, SummonResult


class EggSummonSimulator:
	def __init__(self, player: PlayerModel, config: SummonConfig) -> None:
		self.player = player
		self.config = config

	def summon(self, count: int) -> SummonResult:
		config       = self.config
		summon_model = self.player.pets.summon_model

		if count not in config.possible_summon_count:
			return SummonResult(SummonKind.Pets, count, 0, success=False, error="invalid_summon_count")
		if not config.can_afford(self.player, count):
			return SummonResult(SummonKind.Pets, count, 0, success=False, error="insufficient_currency")

		config.spend(self.player, count)
		pulls: list[SummonPullResult] = []
		total_target = count
		pull_idx     = 0

		while pull_idx < total_target:
			is_bonus = pull_idx >= count
			seed     = summon_model.get_seed()
			rng      = RandomPCG(seed)

			# PCG call #1: StatHelper$$RollStat (ExtraEggChance bonus check)
			if not is_bonus and StatHelper.roll_bonus_summon(self.player, SummonKind.Pets, rng):
				total_target += 1

			# PCG call #2: SummonLevelConfig$$RollRarity
			level_cfg = config.get_level_config(summon_model.level)
			rarity    = level_cfg.roll_rarity(rng)

			# Main PCG discarded; CreateEggModel uses a separate PCG from seed for GUID.
			egg = EggModel(rarity, seed)
			self.player.pets.add_egg(egg)

			pet_name = next(
				(d["Name"] for d in PET_MAPPING.values() if d.get("Rarity") == rarity.value),
				f"Egg({rarity.name})",
			)
			pulls.append(SummonPullResult(rarity, True, pet_name.replace(" ", ""), is_bonus=is_bonus))

			config.advance_progress(summon_model)
			config.advance_seed(summon_model)
			pull_idx += 1

		return SummonResult(SummonKind.Pets, count, len(pulls), pulls=pulls)
