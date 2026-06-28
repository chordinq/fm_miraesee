from __future__ import annotations

from typing import TYPE_CHECKING

from ...shared_game_config import get_unlocked_pet_slot_count
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


class PetEquipAction(PlayerAction):
	action_code = ActionCodes.PetEquip

	def __init__(self, pet_to_equip: str, slot_id: int) -> None:
		super().__init__()
		self.pet_to_equip = pet_to_equip
		self.slot_id = slot_id

	def execute(self, player: PlayerModel, commit: bool = True) -> MetaActionResult:
		collection = player.player_pet_collection_model
		pet = _find_pet_by_guid(collection.pets, self.pet_to_equip)
		if pet is None:
			return ActionResult.DoesNotExist

		if pet.is_equipped and pet.equip_slot == self.slot_id:
			return ActionResult.AlreadyEquipped

		if self.slot_id >= get_unlocked_pet_slot_count(player):
			return ActionResult.NotEnoughResources

		if not commit:
			return ActionResult.Success

		occupant = collection.try_get_pet_in_slot(self.slot_id)
		if occupant is not None:
			occupant.is_equipped = False
			occupant.equip_slot = _EMPTY_EQUIP_SLOT

		pet.is_equipped = True
		pet.equip_slot = self.slot_id
		player.player_power_model.update_power(player, publish_update=True)
		return ActionResult.Success
