"""
ONLY FOR REFERENCE — disabled until game_logic APIs are migrated.
Re-enable by uncommenting the block below.
"""

# from __future__ import annotations
#
# from config import SKILL_LIBRARY, SKILLS_MAPPING
# from core.enums import CombatSkill, Rarity, SummonKind, TechTreeNodeType
# from core.random_pcg import RandomPCG
# from core.game_logic.player_model import PlayerModel, SkillModel
# from core.game_logic.summon_config import SummonConfig
# from core.game_logic.summon_cost import can_afford_summon_batch, spend_summon_batch
# from core.game_logic.stat_helper import StatHelper
# from .summon_base import SummonPullResult, SummonResult
#
#
# def _build_skills_by_rarity() -> dict[str, list[str]]:
# 	pools: dict[str, list[str]] = {r.name: [] for r in Rarity}
# 	for key, data in SKILL_LIBRARY.items():
# 		pools[data["Rarity"]].append(key)
# 	return pools
#
#
# _SKILLS_BY_RARITY: dict[str, list[str]] = _build_skills_by_rarity()
#
#
# class SkillSummonSimulator:
# 	def __init__(self, player: PlayerModel, config: SummonConfig) -> None:
# 		self.player = player
# 		self.config = config
#
# 	def summon(self, count: int) -> SummonResult:
# 		config       = self.config
# 		summon_model = self.player.skills.summon_model
#
# 		if count not in config.possible_summon_count:
# 			return SummonResult(SummonKind.Skills, count, 0, success=False, error="invalid_summon_count")
#
# 		if not can_afford_summon_batch(
# 			self.player, config, TechTreeNodeType.SkillSummonCost, count
# 		):
# 			return SummonResult(SummonKind.Skills, count, 0, success=False, error="insufficient_currency")
#
# 		spend_summon_batch(self.player, config, TechTreeNodeType.SkillSummonCost, count)
# 		pulls: list[SummonPullResult] = []
#
# 		for _ in range(count):
# 			seed = summon_model.get_seed()
# 			rng  = RandomPCG(seed)
#
# 			StatHelper.roll_bonus_summon(self.player, SummonKind.Skills, rng)
#
# 			level_cfg = config.get_level_config(summon_model.level)
# 			rarity    = level_cfg.roll_rarity(rng)
#
# 			skill_name = rng.choice(_SKILLS_BY_RARITY[rarity.name])
# 			pulls.append(self._apply_pull(rarity, skill_name))
#
# 			config.advance_progress(summon_model)
# 			config.advance_seed(summon_model)
#
# 		return SummonResult(SummonKind.Skills, count, len(pulls), pulls=pulls)
#
# 	def _resolve_skill(self, skill_name: str) -> tuple:
# 		from core.enums import Rarity
#
# 		data = SKILL_LIBRARY[skill_name]
# 		combat_skill = CombatSkill[data["Type"]]
# 		for mapping in SKILLS_MAPPING.values():
# 			if mapping.get("Enum") == combat_skill.value:
# 				return combat_skill, Rarity(mapping["Rarity"]), int(mapping["Idx"])
# 		lib_rarity = data.get("Rarity", "Common")
# 		return combat_skill, Rarity[lib_rarity], 0
#
# 	def _apply_pull(self, rarity, skill_name: str) -> SummonPullResult:
# 		combat_skill, skill_rarity, idx = self._resolve_skill(skill_name)
# 		collection = self.player.skills
# 		detail = skill_name.replace(" ", "")
#
# 		if combat_skill in collection.skills:
# 			collection.skills[combat_skill].add_shards(1)
# 			return SummonPullResult(rarity, False, detail)
#
# 		collection.skills[combat_skill] = SkillModel(skill_rarity, idx)
# 		return SummonPullResult(rarity, True, detail)
