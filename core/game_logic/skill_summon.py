# core/game_logic/skill_summon.py
"""
Skill summon simulator.

Per pull (C# SkillSummonFinalizedAction$$Execute):
  rng  = RandomPCG(seed)
  StatHelper$$RollStat -> NextFixedD6  (1 PCG call -- result unused for skill bonus)
  rarity = SummonLevelConfig$$RollRarity(rng)
  skill  = RandomPCG$$Choice(skills_of_rarity)
  seed  += 1
"""

from __future__ import annotations

from configs import SKILL_LIBRARY, SKILL_MAPPING
from core.enums import CombatSkill, SummonKind
from core.enums import RARITY_NAMES
from core.random_pcg import RandomPCG
from core.game_logic.player_model.PlayerModel import PlayerModel
from core.game_logic.player_model.SkillModel import SkillModel
from core.game_logic.summon_config import SummonConfig
from core.game_logic.stat_helper import StatHelper
from core.game_logic.summon_base import SummonPullResult, SummonResult


def _build_skills_by_rarity() -> dict[str, list[str]]:
	pools: dict[str, list[str]] = {name: [] for name in RARITY_NAMES}
	for key, data in SKILL_LIBRARY.items():
		pools[data["Rarity"]].append(key)
	return pools


_SKILLS_BY_RARITY: dict[str, list[str]] = _build_skills_by_rarity()


class SkillSummonSimulator:
	def __init__(self, player: PlayerModel, config: SummonConfig) -> None:
		self.player = player
		self.config = config

	def summon(self, count: int) -> SummonResult:
		config       = self.config
		summon_model = self.player.skills.summon_model

		if count not in config.possible_summon_count:
			return SummonResult(SummonKind.Skills, count, 0, success=False, error="invalid_summon_count")

		config.spend(self.player, count)
		pulls: list[SummonPullResult] = []

		for _ in range(count):
			seed = summon_model.get_seed()
			rng  = RandomPCG(seed)

			# PCG call #1: StatHelper$$RollStat bonus check (always consumed; result unused for skills)
			StatHelper.roll_bonus_summon(self.player, SummonKind.Skills, rng)

			# PCG call #2: SummonLevelConfig$$RollRarity
			level_cfg = config.get_level_config(summon_model.level)
			rarity    = level_cfg.roll_rarity(rng)

			# PCG calls #3..(2+N): RandomPCG$$Choice from pool of N skills
			skill_name = rng.choice(_SKILLS_BY_RARITY[rarity.name])
			pulls.append(self._apply_pull(rarity, skill_name))

			config.advance_progress(summon_model)
			config.advance_seed(summon_model)

		return SummonResult(SummonKind.Skills, count, len(pulls), pulls=pulls)

	def _resolve_skill(self, skill_name: str) -> tuple:
		from core.enums import Rarity

		data = SKILL_LIBRARY[skill_name]
		combat_skill = CombatSkill[data["Type"]]
		for mapping in SKILL_MAPPING.values():
			if mapping.get("Enum") == combat_skill.value:
				return combat_skill, Rarity(mapping["Rarity"]), int(mapping["Idx"])
		lib_rarity = data.get("Rarity", "Common")
		return combat_skill, Rarity[lib_rarity], 0

	def _apply_pull(self, rarity, skill_name: str) -> SummonPullResult:
		combat_skill, skill_rarity, idx = self._resolve_skill(skill_name)
		collection = self.player.skills
		detail = skill_name.replace(" ", "")

		if combat_skill in collection.skills:
			collection.skills[combat_skill].add_shards(1)
			return SummonPullResult(rarity, False, detail)

		collection.skills[combat_skill] = SkillModel(skill_rarity, idx)
		return SummonPullResult(rarity, True, detail)
