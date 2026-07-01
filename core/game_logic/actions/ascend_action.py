from __future__ import annotations

from typing import TYPE_CHECKING

from ..enums import AscendableType
from ..player.ascension_model import (
	ascend,
	ascension_conditions_met,
	ascensions_maxed,
	get_ascension_cost_for_type as get_ascension_cost,
)
from ..player.player_currency_model import can_afford
from .action_codes import ActionCodes
from .action_result import ActionResult, MetaActionResult
from .player_action import PlayerAction

if TYPE_CHECKING:
	from ..player.player_model import PlayerModel


class AscendAction(PlayerAction):
	action_code = ActionCodes.Ascend

	def __init__(self, ascendable_type: AscendableType) -> None:
		super().__init__()
		self.ascendable_type = ascendable_type

	def execute(self, player: PlayerModel, commit: bool = True) -> MetaActionResult:
		if ascensions_maxed(self.ascendable_type, player):
			return ActionResult.MaxLevelReached

		if not ascension_conditions_met(self.ascendable_type, player):
			return ActionResult.LevelTooLow

		price = get_ascension_cost(self.ascendable_type, player)
		can_pay, spend_ctx = can_afford(player, price.currency, price.amount)
		if not can_pay or spend_ctx is None:
			return ActionResult.NotEnoughResources

		if not commit:
			return ActionResult.Success

		spend_ctx.spend("Ascend")
		ascend(self.ascendable_type, player)
		return ActionResult.Success
