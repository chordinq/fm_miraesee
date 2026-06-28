from __future__ import annotations

from typing import TYPE_CHECKING

from ..action_codes import ActionCodes
from ..action_result import ActionResult, MetaActionResult
from ..player_action import PlayerAction

if TYPE_CHECKING:
	from ...player.player_model import PlayerModel
	from ...player.player_pet_collection_model import PlayerPetModel

_EMPTY_EQUIP_SLOT = -1


def _find_pet_by_guid(pets: list[PlayerPetModel], pet_guid: str) -> PlayerPetModel | None:
	for pet in pets:
		if pet.guid == pet_guid:
			return pet
	return None


class PetUnEquipAction(PlayerAction):
	action_code = ActionCodes.PetUnEquip

	def __init__(self, pet_to_unequip: str) -> None:
		super().__init__()
		self.pet_to_unequip = pet_to_unequip

	def execute(self, player: PlayerModel, commit: bool = True) -> MetaActionResult:
		pet = _find_pet_by_guid(player.player_pet_collection_model.pets, self.pet_to_unequip)
		if pet is None:
			return ActionResult.DoesNotExist

		if not pet.is_equipped:
			return ActionResult.NotEquipped

		if not commit:
			return ActionResult.Success

		pet.is_equipped = False
		pet.equip_slot = _EMPTY_EQUIP_SLOT
		player.player_power_model.update_power(player, publish_update=True)
		return ActionResult.Success
