from __future__ import annotations

from typing import TYPE_CHECKING

from ...enums import CurrencyType, GemSkipTarget
from ...player.player_currency_model import can_afford
from ..action_codes import ActionCodes
from ..action_result import ActionResult, MetaActionResult
from ..player_action import PlayerAction

if TYPE_CHECKING:
	from ...player.player_model import PlayerModel


class ForgeGemSkipAction(PlayerAction):
	action_code = ActionCodes.ForgeGemSkip

	def execute(self, player: PlayerModel, commit: bool = True) -> MetaActionResult:
		forge = player.player_forge_model
		timer = forge.forge_upgrade_timer
		if timer is None:
			return ActionResult.NotStarted

		forge_config = player.game_config.forge_config
		if (
			forge.forge_level < forge_config.free_forge_upgrades
			and forge.ascension_model.current_level == 0
		):
			gem_cost = 0
		else:
			gem_cost = timer.calculate_gem_skip_cost(player, GemSkipTarget.Forge)

		affordable, spend_context = can_afford(player, CurrencyType.Gems, gem_cost)
		if not affordable or spend_context is None:
			return ActionResult.NotEnoughResources

		if not commit:
			return ActionResult.Success

		spend_context.spend("ForgeGemSkip")
		timer.skip_to_end(player)
		return ActionResult.Success
