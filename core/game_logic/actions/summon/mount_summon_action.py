from __future__ import annotations
from typing import TYPE_CHECKING
from ...enums import Rarity, StatType
from ....random_pcg import RandomPCG
from ...player.player_mount_collection_model import MountId, create_mount_from_ids
from ...stats.stat_helper import StatHelper
from ...stats.stat_target import MountStatTarget
from ..action_codes import ActionCodes
from ..action_result import ActionResult, MetaActionResult
from ..player_action import PlayerAction

if TYPE_CHECKING:
	from ...player.player_model import PlayerModel
	from ...player.player_mount_collection_model import PlayerMountModel


class SummonedMountsInfo:
	def __init__(self, model: PlayerMountModel, is_new: bool) -> None:
		self.mount_model = model
		self.is_new = is_new


class MountSummonFinalizedAction(PlayerAction):
	action_code = ActionCodes.MountSummonFinalized

	def __init__(self, count: int = 1) -> None:
		super().__init__()
		self.count = count
		self.summoned: list[SummonedMountsInfo] = []

	def execute(self, player: PlayerModel, commit: bool = True) -> MetaActionResult:
		self.summoned = []
		game_config = player.game_config
		summon_config = game_config.mount_summon_config
		collection = player.player_mount_collection_model
		summon_model = collection.summon_model

		if self.count not in summon_config.possible_summon_count:
			return ActionResult.DoesNotExist

		can_afford, spend_context = summon_config.can_afford_summon(player, self.count)
		if not can_afford or spend_context is None:
			return ActionResult.NotEnoughResources

		if not commit:
			return ActionResult.Success

		spend_context.spend("MountSummon")
		freebie_target = MountStatTarget()
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
			candidates = _mount_ids_for_rarity(game_config.mount_library, rolled_rarity)
			if not candidates:
				return ActionResult.DoesNotExist

			mount = create_mount_from_ids(player, candidates, rng)
			is_new = all(
				existing.mount_id != mount.mount_id
				for existing in collection.player_mount_models
			)
			collection.player_mount_models.append(mount)
			self.summoned.append(SummonedMountsInfo(mount, is_new))

			summon_model.increment_summon_count(summon_config)
			i += 1

		return ActionResult.Success


def _mount_ids_for_rarity(
	mount_library: dict[MountId, dict],
	rarity: Rarity,
) -> list[MountId]:
	return [mount_id for mount_id in mount_library if mount_id.rarity == rarity]
