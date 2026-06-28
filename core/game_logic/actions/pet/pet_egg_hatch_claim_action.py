from __future__ import annotations

from typing import TYPE_CHECKING

from ..action_codes import ActionCodes
from ..action_result import ActionResult, MetaActionResult
from ..player_action import PlayerAction
from .pet_egg_hatch_action import _find_egg_by_guid

if TYPE_CHECKING:
	from ...player.player_model import PlayerModel


class PetEggHatchClaimAction(PlayerAction):
	action_code = ActionCodes.PetEggHatchClaim

	def __init__(self, egg_guid: str) -> None:
		super().__init__()
		self.egg_guid = egg_guid

	def execute(self, player: PlayerModel, commit: bool = True) -> MetaActionResult:
		egg = _find_egg_by_guid(player.player_pet_collection_model.eggs, self.egg_guid)
		if egg is None:
			return ActionResult.DoesNotExist

		if egg.timer is None or not egg.is_equipped:
			return ActionResult.NotStarted

		if not egg.timer.has_ended(player):
			return ActionResult.NotReady

		if not commit:
			return ActionResult.Success

		return ActionResult.Success
