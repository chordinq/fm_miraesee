from __future__ import annotations
from typing import TYPE_CHECKING
from ....random_pcg import RandomPCG
from ...enums import StatType
from ...player.player_pet_collection_model import (
	HatchedPetInfo,
	PlayerEggModel,
	create_pet_from_ids,
	pet_ids_for_rarity,
)
from ...player.timer_model import TimerModel
from ...stats.stat_helper import StatHelper
from ...stats.stat_target import EggStatTarget
from ..action_codes import ActionCodes
from ..action_result import ActionResult, MetaActionResult
from ..player_action import PlayerAction

if TYPE_CHECKING:
	from ...player.player_model import PlayerModel


def _find_egg_by_guid(eggs: list[PlayerEggModel], egg_guid: str) -> PlayerEggModel | None:
	for egg in eggs:
		if egg.guid == egg_guid:
			return egg
	return None


class PetEggHatchStartAction(PlayerAction):
	action_code = ActionCodes.PetEggHatchStart

	def __init__(self, egg_guid: str, slot_index: int) -> None:
		super().__init__()
		self.egg_guid = egg_guid
		self.slot_index = slot_index

	def execute(self, player: PlayerModel, commit: bool = True) -> MetaActionResult:
		collection = player.player_pet_collection_model
		egg = _find_egg_by_guid(collection.eggs, self.egg_guid)
		if egg is None:
			return ActionResult.DoesNotExist

		if (
			egg.timer is not None
			or egg.is_equipped
			or egg.equip_slot >= 0
		):
			return ActionResult.AlreadyInProgress

		if not collection.is_hatch_slot_available(self.slot_index):
			return ActionResult.HatchingSlotUnavailable

		if not commit:
			return ActionResult.Success

		egg_config = player.game_config.egg_library.get(egg.rarity)
		if egg_config is None:
			raise ValueError(f"No EggConfig for rarity: {egg.rarity!r}")

		base_duration = float(egg_config.get("HatchTime", 0))
		target = EggStatTarget(egg.rarity)
		duration = round(
			StatHelper.calculate_value(
				player,
				StatType.TimerSpeed,
				target,
				base_duration,
			)
		)
		egg.timer = TimerModel(player, duration)
		egg.equip_slot = self.slot_index
		egg.is_equipped = True
		return ActionResult.Success


class PetEggHatchFinalizedAction(PlayerAction):
	action_code = ActionCodes.PetEggHatchFinalized

	def __init__(self, egg_guid: str) -> None:
		super().__init__()
		self.egg_guid = egg_guid
		self.hatched: HatchedPetInfo | None = None

	def execute(self, player: PlayerModel, commit: bool = True) -> MetaActionResult:
		collection = player.player_pet_collection_model
		egg = _find_egg_by_guid(collection.eggs, self.egg_guid)
		if egg is None:
			return ActionResult.DoesNotExist

		if not commit:
			return ActionResult.Success

		pet_ids = pet_ids_for_rarity(player.game_config.pet_library, egg.rarity)
		if not pet_ids:
			return ActionResult.DoesNotExist

		rng = RandomPCG.create_from_seed(egg.seed)
		pet = create_pet_from_ids(player, pet_ids, rng, None)
		is_new = not any(existing.pet_id == pet.pet_id for existing in collection.pets)
		previous_slot = egg.equip_slot

		collection.pets.append(pet)
		collection.eggs.remove(egg)
		self.hatched = HatchedPetInfo(pet, is_new, previous_slot)
		return ActionResult.Success
