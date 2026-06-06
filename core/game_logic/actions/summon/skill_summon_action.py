from __future__ import annotations
from typing import TYPE_CHECKING
from ...enums import CombatSkill, Rarity, StatType
from ....random_pcg import RandomPCG
from ...stats.stat_helper import StatHelper
from ...stats.stat_target import ActiveSkillStatTarget
from ..action_codes import ActionCodes
from ..action_result import ActionResult, MetaActionResult
from ..player_action import PlayerAction
from ...player.player_skill_collection_model import PlayerSkillModel

if TYPE_CHECKING:
	from ...player.player_model import PlayerModel


class SummonedSkillInfo:
	def __init__(self, model: PlayerSkillModel, is_new: bool) -> None:
		self.type = model.type
		self.is_new = is_new


class SkillSummonAction(PlayerAction):
	action_code = ActionCodes.SkillSummon
	finalized_action_code = ActionCodes.SkillSummonFinalized

	def __init__(self, count: int = 1) -> None:
		super().__init__()
		self.count = count
		self.summoned: list[SummonedSkillInfo] = []

	def execute(self, player: PlayerModel, commit: bool = True) -> MetaActionResult:
		self.summoned = []
		game_config = player.game_config
		summon_config = game_config.skill_summon_config
		collection = player.player_skill_collection_model
		summon_model = collection.summon_model

		if self.count not in summon_config.possible_summon_count:
			return ActionResult.DoesNotExist

		can_afford, spend_context = summon_config.can_afford_summon(player, self.count)
		if not can_afford or spend_context is None:
			return ActionResult.NotEnoughResources

		if not commit:
			return ActionResult.Success

		spend_context.spend("SkillSummon")
		freebie_target = ActiveSkillStatTarget()
		effective_count = self.count
		i = 0
		while i < effective_count:
			rng = RandomPCG.create_from_seed(summon_model.seed)
			if i < self.count:
				if StatHelper.roll_stat(
					player,
					StatType.FreebieChance,
					freebie_target,
					rng,
				):
					effective_count += 1

			level_cfg = summon_config.levels[summon_model.level]
			rolled_rarity = level_cfg.roll_rarity(rng)
			candidates = _skills_for_rarity(game_config.skill_library, rolled_rarity)
			if not candidates:
				return ActionResult.DoesNotExist

			combat_skill = rng.choice(iter(candidates))
			existing = collection.player_skills.get(combat_skill)
			if existing is None:
				skill = PlayerSkillModel(combat_skill)
				collection.player_skills[combat_skill] = skill
				self.summoned.append(SummonedSkillInfo(skill, True))
			else:
				existing.add_shards(1, None)
				self.summoned.append(SummonedSkillInfo(existing, False))

			summon_model.increment_summon_count(summon_config)
			i += 1

		if any(info.is_new for info in self.summoned):
			player.player_power_model.update_power(player, publish_update=False)

		return ActionResult.Success


def _skills_for_rarity(
	skill_library: dict[CombatSkill, dict],
	rarity: Rarity,
) -> list[CombatSkill]:
	result: list[CombatSkill] = []
	for combat_skill, config in skill_library.items():
		rarity_name = config.get("Rarity")
		if rarity_name is None:
			continue
		try:
			skill_rarity = Rarity[rarity_name] if isinstance(rarity_name, str) else Rarity(int(rarity_name))
		except (KeyError, ValueError):
			continue
		if skill_rarity == rarity:
			result.append(combat_skill)
	return result
