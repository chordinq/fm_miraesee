from __future__ import annotations

from typing import TYPE_CHECKING

from ...enums import CombatSkill
from ..action_codes import ActionCodes
from ..action_result import ActionResult, MetaActionResult
from ..player_action import PlayerAction
from ...shared_game_config import get_unlocked_skill_slot_count

if TYPE_CHECKING:
	from ...player.player_model import PlayerModel

_EMPTY_EQUIP_SLOT = -1


class SkillEquipAction(PlayerAction):
	action_code = ActionCodes.SkillEquip

	def __init__(self, skill_to_equip: CombatSkill, slot_id: int) -> None:
		super().__init__()
		self.skill_to_equip = skill_to_equip
		self.slot_id = slot_id

	def execute(self, player: PlayerModel, commit: bool = True) -> MetaActionResult:
		collection = player.player_skill_collection_model
		skill_model = collection.try_get_skill(self.skill_to_equip)
		if skill_model is None:
			return ActionResult.DoesNotExist

		if skill_model.is_equipped and skill_model.equip_slot == self.slot_id:
			return ActionResult.AlreadyEquipped

		unlocked_slot_count = get_unlocked_skill_slot_count(player)
		if self.slot_id >= unlocked_slot_count:
			return ActionResult.NotEnoughResources

		if not commit:
			return ActionResult.Success

		occupant = collection.try_get_skill_in_slot(self.slot_id)
		if occupant is not None:
			occupant.is_equipped = False
			occupant.equip_slot = _EMPTY_EQUIP_SLOT

		skill_model.is_equipped = True
		skill_model.equip_slot = self.slot_id
		return ActionResult.Success
