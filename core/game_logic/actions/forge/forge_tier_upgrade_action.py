from __future__ import annotations

from typing import TYPE_CHECKING

from ...enums import CurrencyType
from ...forge_extensions import get_forge_tier_upgrade_cost
from ...player.player_currency_model import can_afford
from ..action_codes import ActionCodes
from ..action_result import ActionResult, MetaActionResult
from ..player_action import PlayerAction

if TYPE_CHECKING:
	from ...player.player_model import PlayerModel


class ForgeTierUpgradeAction(PlayerAction):
	action_code = ActionCodes.ForgeTierUpgrade

	def execute(self, player: PlayerModel, commit: bool = True) -> MetaActionResult:
		forge = player.player_forge_model
		if forge.forge_upgrade_timer is not None:
			return ActionResult.AlreadyInProgress

		if forge.forge_tiers_maxed(player):
			return ActionResult.MaxLevelReached

		cost = get_forge_tier_upgrade_cost(player)
		affordable, spend_context = can_afford(player, CurrencyType.Coins, cost)
		if not affordable or spend_context is None:
			return ActionResult.NotEnoughResources

		if not commit:
			return ActionResult.Success

		spend_context.spend("ForgeTierUpgrade")
		forge.current_forge_tier_level += 1
		return ActionResult.Success
