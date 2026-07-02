from __future__ import annotations

from typing import TYPE_CHECKING

from ...enums import TechTreeType
from ...player.timer_model import TimerModel
from ..action_codes import ActionCodes
from ..action_result import ActionResult, MetaActionResult
from ..player_action import PlayerAction

if TYPE_CHECKING:
	from ...player.player_model import PlayerModel


class TechTreeNodeUpgradeClaimAction(PlayerAction):
	action_code = ActionCodes.TechTreeNodeUpgradeClaim

	def __init__(self, tree_type: TechTreeType, node_id: int) -> None:
		super().__init__()
		self.tree_type = tree_type
		self.node_id = node_id

	def execute(self, player: PlayerModel, commit: bool = True) -> MetaActionResult:
		techtree = player.player_techtree_model
		node_model = techtree.get_node(self.tree_type, self.node_id)
		if node_model is None:
			return ActionResult.DoesNotExist

		timer = node_model.node_upgrade_timer_model
		if timer.start_time <= 0:
			return ActionResult.NotStarted

		if not timer.has_ended(player):
			return ActionResult.NotReady

		if not commit:
			return ActionResult.Success

		node_model.level += 1
		node_model.node_upgrade_timer_model = TimerModel(
			start_time=0,
			end_time=0,
			duration=0,
		)
		player.player_power_model.update_power(player)
		return ActionResult.Success
