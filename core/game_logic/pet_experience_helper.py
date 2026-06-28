from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from .player.player_model import PlayerModel
	from .player.player_pet_collection_model import PlayerPetModel


def get_pet_total_xp(pet: PlayerPetModel, player: PlayerModel) -> int:
	"""IL: PetExperienceHelper.GetPetTotalXp."""
	return pet.get_total_xp(player)
