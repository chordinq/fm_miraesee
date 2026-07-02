from __future__ import annotations

from typing import TYPE_CHECKING

from ...enums import CurrencyType, GemSkipTarget, TechTreeType
from ...player.player_currency_model import can_afford
from ..action_codes import ActionCodes
from ..action_result import ActionResult, MetaActionResult
from ..player_action import PlayerAction

if TYPE_CHECKING:
	from ...player.player_model import PlayerModel


class TechTreeNodeUpgradeGemSkipAction(PlayerAction):
	action_code = ActionCodes.TechTreeNodeUpgradeGemSkip

	def __init__(self, tree_type: TechTreeType, node_id: int) -> None:
		super().__init__()
		self.tree_type = tree_type
		self.node_id = node_id

	def execute(self, player: PlayerModel, commit: bool = True) -> MetaActionResult:
		node_model = player.player_techtree_model.get_node(self.tree_type, self.node_id)
		if node_model is None:
			return ActionResult.DoesNotExist

		timer = node_model.node_upgrade_timer_model
		if timer.start_time <= 0:
			return ActionResult.NotStarted

		gem_cost = timer.calculate_gem_skip_cost(player, GemSkipTarget.TechTree)
		affordable, spend_context = can_afford(player, CurrencyType.Gems, gem_cost)
		if not affordable or spend_context is None:
			return ActionResult.NotEnoughResources

		if not commit:
			return ActionResult.Success

		spend_context.spend("TechTreeNodeUpgradeGemSkip")
		timer.skip_to_end(player)
		return ActionResult.Success
