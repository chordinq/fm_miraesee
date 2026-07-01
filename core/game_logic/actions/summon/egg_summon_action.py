from __future__ import annotations
from typing import TYPE_CHECKING
from ...enums import StatType
from ....random_pcg import RandomPCG
from ...stats.stat_helper import StatHelper
from ...stats.stat_target import EggStatTarget
from ..action_codes import ActionCodes
from ..action_result import ActionResult, MetaActionResult
from ..player_action import PlayerAction

if TYPE_CHECKING:
	from ...player.player_model import PlayerModel
	from ...player.player_pet_collection_model import PlayerEggModel


class SummonedEggInfo:
	def __init__(self, model: PlayerEggModel, is_new: bool) -> None:
		self.egg_model = model
		self.is_new = is_new


class EggSummonFinalizedAction(PlayerAction):
	action_code = ActionCodes.EggSummonFinalized

	def __init__(self, count: int = 1) -> None:
		super().__init__()
		self.count = count
		self.summoned: list[SummonedEggInfo] = []

	def execute(self, player: PlayerModel, commit: bool = True) -> MetaActionResult:
		self.summoned = []
		game_config = player.game_config
		summon_config = game_config.egg_summon_config
		collection = player.player_pet_collection_model
		summon_model = collection.summon_model

		if self.count not in summon_config.possible_summon_count:
			return ActionResult.DoesNotExist

		can_afford, spend_context = summon_config.can_afford_summon(player, self.count)
		if not can_afford or spend_context is None:
			return ActionResult.NotEnoughResources

		if not commit:
			return ActionResult.Success

		spend_context.spend("EggSummon")
		freebie_target = EggStatTarget()
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
			egg = collection.create_egg_model(rolled_rarity, summon_model.seed)
			is_new = all(existing.rarity != rolled_rarity for existing in collection.eggs)
			collection.eggs.append(egg)
			self.summoned.append(SummonedEggInfo(egg, is_new))

			summon_model.increment_summon_count(summon_config)
			i += 1

		return ActionResult.Success
