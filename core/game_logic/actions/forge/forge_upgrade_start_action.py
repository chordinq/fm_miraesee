from __future__ import annotations

from typing import TYPE_CHECKING

from ...enums import StatType
from ...stats.stat_helper import StatHelper
from ...stats.stat_target import ForgeStatTarget
from ..action_codes import ActionCodes
from ..action_result import ActionResult, MetaActionResult
from ..player_action import PlayerAction
from ...player.timer_model import TimerModel

if TYPE_CHECKING:
	from ...player.player_model import PlayerModel


class ForgeUpgradeStartAction(PlayerAction):
	action_code = ActionCodes.ForgeUpgradeStart

	def execute(self, player: PlayerModel, commit: bool = True) -> MetaActionResult:
		forge = player.player_forge_model
		if not forge.forge_tiers_maxed(player):
			return ActionResult.LevelTooLow

		if forge.forge_levels_maxed(player):
			return ActionResult.MaxLevelReached

		if forge.forge_upgrade_timer is not None:
			return ActionResult.AlreadyInProgress

		if not commit:
			return ActionResult.Success

		next_level = forge.forge_level + 1
		upgrade_row = player.game_config.forge_upgrade_library.get(next_level)
		if upgrade_row is None:
			return ActionResult.UnknownError

		base_duration = float(upgrade_row.get("Duration", 0))
		target = ForgeStatTarget()
		duration = StatHelper.calculate_value(
			player,
			StatType.TimerSpeed,
			target,
			base_duration,
		)
		forge.current_forge_tier_level = 0
		forge.forge_upgrade_timer = TimerModel(player, duration)
		return ActionResult.Success
