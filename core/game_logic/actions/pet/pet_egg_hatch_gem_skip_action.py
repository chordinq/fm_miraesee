from __future__ import annotations

from typing import TYPE_CHECKING

from ...enums import CurrencyType, GemSkipTarget
from ...player.player_currency_model import can_afford
from ..action_codes import ActionCodes
from ..action_result import ActionResult, MetaActionResult
from ..player_action import PlayerAction
from .pet_egg_hatch_action import _find_egg_by_guid

if TYPE_CHECKING:
	from ...player.player_model import PlayerModel


class PetEggHatchGemSkipAction(PlayerAction):
	action_code = ActionCodes.PetEggHatchGemSkip

	def __init__(self, egg_guid: str) -> None:
		super().__init__()
		self.egg_guid = egg_guid

	def execute(self, player: PlayerModel, commit: bool = True) -> MetaActionResult:
		collection = player.player_pet_collection_model
		egg = _find_egg_by_guid(collection.eggs, self.egg_guid)
		if egg is None:
			return ActionResult.DoesNotExist

		timer = egg.timer
		if timer is None:
			return ActionResult.NotStarted

		gem_cost = timer.calculate_gem_skip_cost(player, GemSkipTarget.PetEgg)
		affordable, spend_context = can_afford(player, CurrencyType.Gems, gem_cost)
		if not affordable or spend_context is None:
			return ActionResult.NotEnoughResources

		if not commit:
			return ActionResult.Success

		spend_context.spend("PetEggHatchGemSkip")
		timer.skip_to_end(player)
		return ActionResult.Success
