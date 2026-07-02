from __future__ import annotations

from typing import TYPE_CHECKING

from ...enums import CurrencyType, TechTreeNodeType, TechTreeType
from ...player.player_currency_model import can_afford
from ...player.player_techtree_model import (
	TechTreeNodeModel,
	find_position_node,
	resolve_upgrade_level_info,
	upgrade_level_index,
)
from ...player.timer_model import TimerModel
from ..action_codes import ActionCodes
from ..action_result import ActionResult, MetaActionResult
from ..player_action import PlayerAction

if TYPE_CHECKING:
	from ...player.player_model import PlayerModel


class TechTreeNodeUpgradeStartAction(PlayerAction):
	action_code = ActionCodes.TechTreeNodeUpgradeStart

	def __init__(self, tree_type: TechTreeType, node_id: int) -> None:
		super().__init__()
		self.tree_type = tree_type
		self.node_id = node_id

	def execute(self, player: PlayerModel, commit: bool = True) -> MetaActionResult:
		techtree = player.player_techtree_model
		game_config = player.game_config

		node_info = find_position_node(game_config, self.tree_type, self.node_id)
		if node_info is None:
			return ActionResult.DoesNotExist

		try:
			node_type = TechTreeNodeType[node_info["Type"]]
		except KeyError:
			return ActionResult.DoesNotExist

		lib_entry = game_config.tech_tree_library.get(node_type)
		if lib_entry is None:
			return ActionResult.DoesNotExist

		level_max = int(lib_entry.get("MaxLevel", 0))
		tier = int(node_info.get("Tier", 0))

		try:
			if not techtree.node_requirements_met(player, self.tree_type, self.node_id):
				return ActionResult.Locked
		except ValueError:
			return ActionResult.DoesNotExist

		node_model = techtree.get_node(self.tree_type, self.node_id)
		if node_model is not None:
			if node_model.level >= level_max - 1:
				return ActionResult.MaxLevelReached
			timer = node_model.node_upgrade_timer_model
			if timer.start_time > 0:
				return ActionResult.AlreadyInProgress

		if techtree.is_any_node_research_in_progress(player):
			return ActionResult.AlreadyInProgress

		level_index = upgrade_level_index(node_model)
		upgrade_info = resolve_upgrade_level_info(player, tier, level_index)
		if upgrade_info is None:
			return ActionResult.DoesNotExist

		upgrade_cost, duration_seconds = upgrade_info
		affordable, spend_context = can_afford(
			player,
			CurrencyType.TechPotions,
			upgrade_cost,
		)
		if not affordable or spend_context is None:
			return ActionResult.NotEnoughResources

		if not commit:
			return ActionResult.Success

		if node_model is None:
			techtree.set_node_level(self.tree_type, self.node_id, -1)
			node_model = techtree.get_node(self.tree_type, self.node_id)
			if node_model is None:
				return ActionResult.UnknownError

		spend_context.spend("TechTreeNodeUpgradeStart")
		node_model.node_upgrade_timer_model = TimerModel(player, float(duration_seconds))
		return ActionResult.Success
