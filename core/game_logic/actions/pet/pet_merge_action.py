from __future__ import annotations

from typing import TYPE_CHECKING

from ..action_codes import ActionCodes
from ..action_result import ActionResult, MetaActionResult
from ..player_action import PlayerAction

if TYPE_CHECKING:
	from ...player.player_model import PlayerModel
	from ...player.player_pet_collection_model import PlayerEggModel, PlayerPetModel


def _find_pet_by_guid(pets: list[PlayerPetModel], pet_guid: str) -> PlayerPetModel | None:
	for pet in pets:
		if pet.guid == pet_guid:
			return pet
	return None


def _find_egg_by_guid(eggs: list[PlayerEggModel], egg_guid: str) -> PlayerEggModel | None:
	for egg in eggs:
		if egg.guid == egg_guid:
			return egg
	return None


class PetMergeAction(PlayerAction):
	action_code = ActionCodes.PetMerge

	def __init__(
		self,
		pet_merge_target: str,
		pet_merge_sources: list[str] | None = None,
		egg_merge_sources: list[str] | None = None,
	) -> None:
		super().__init__()
		self.pet_merge_target = pet_merge_target
		self.pet_merge_sources = list(pet_merge_sources or [])
		self.egg_merge_sources = list(egg_merge_sources or [])

	def execute(self, player: PlayerModel, commit: bool = True) -> MetaActionResult:
		from ...player.player_pet_collection_model import PlayerPetModel

		collection = player.player_pet_collection_model
		target = _find_pet_by_guid(collection.pets, self.pet_merge_target)
		if target is None:
			return ActionResult.DoesNotExist

		source_pets: list[PlayerPetModel] = []
		for pet_guid in self.pet_merge_sources:
			pet = _find_pet_by_guid(collection.pets, pet_guid)
			if pet is None:
				return ActionResult.DoesNotExist
			source_pets.append(pet)

		source_eggs: list[PlayerEggModel] = []
		for egg_guid in self.egg_merge_sources:
			egg = _find_egg_by_guid(collection.eggs, egg_guid)
			if egg is None:
				return ActionResult.DoesNotExist
			source_eggs.append(egg)

		for pet in source_pets:
			if pet.is_locked:
				return ActionResult.Locked

		merged_xp = sum(pet.get_total_xp(player) for pet in source_pets)
		merged_xp += sum(egg.get_xp(player) for egg in source_eggs)
		total_xp = target.get_total_xp(player) + merged_xp
		new_level, new_experience = PlayerPetModel.calculate_level_and_xp(
			player,
			target,
			total_xp,
		)

		if not commit:
			return ActionResult.Success

		for pet in source_pets:
			collection.pets.remove(pet)
		for egg in source_eggs:
			collection.eggs.remove(egg)

		target.level = new_level
		target.experience = new_experience
		player.player_power_model.update_power(player, publish_update=True)
		return ActionResult.Success
