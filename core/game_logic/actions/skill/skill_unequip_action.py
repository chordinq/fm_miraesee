from __future__ import annotations

from typing import TYPE_CHECKING

from ...enums import CombatSkill
from ..action_codes import ActionCodes
from ..action_result import ActionResult, MetaActionResult
from ..player_action import PlayerAction

if TYPE_CHECKING:
	from ...player.player_model import PlayerModel

_EMPTY_EQUIP_SLOT = -1


class SkillUnEquipAction(PlayerAction):
	action_code = ActionCodes.SkillUnEquip

	def __init__(self, skill_to_unequip: CombatSkill) -> None:
		super().__init__()
		self.skill_to_unequip = skill_to_unequip

	def execute(self, player: PlayerModel, commit: bool = True) -> MetaActionResult:
		skill_model = player.player_skill_collection_model.try_get_skill(
			self.skill_to_unequip
		)
		if skill_model is None:
			return ActionResult.DoesNotExist

		if not skill_model.is_equipped:
			return ActionResult.NotEquipped

		if not commit:
			return ActionResult.Success

		skill_model.is_equipped = False
		skill_model.equip_slot = _EMPTY_EQUIP_SLOT
		return ActionResult.Success
