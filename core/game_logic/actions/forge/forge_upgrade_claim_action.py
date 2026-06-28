from __future__ import annotations

from typing import TYPE_CHECKING

from ..action_codes import ActionCodes
from ..action_result import ActionResult, MetaActionResult
from ..player_action import PlayerAction

if TYPE_CHECKING:
	from ...player.player_model import PlayerModel


class ForgeUpgradeClaimAction(PlayerAction):
	action_code = ActionCodes.ForgeUpgradeClaim

	def execute(self, player: PlayerModel, commit: bool = True) -> MetaActionResult:
		forge = player.player_forge_model
		timer = forge.forge_upgrade_timer
		if timer is None:
			return ActionResult.NotStarted

		if not timer.has_ended(player):
			return ActionResult.NotReady

		if forge.forge_levels_maxed(player):
			return ActionResult.MaxLevelReached

		if not commit:
			return ActionResult.Success

		forge.forge_upgrade_timer = None
		forge.forge_level += 1
		return ActionResult.Success
