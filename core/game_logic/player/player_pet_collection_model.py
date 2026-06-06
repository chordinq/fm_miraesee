from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..enums import AscendableType, Rarity
from ..random_pcg import RandomPCG
from ..stats import SecondaryStats
from .ascension_model import AscensionModel
from .summon_model import SummonModel
from .timer_model import TimerModel

_EMPTY_EGG_SLOT = -1


@dataclass(frozen=True)
class PetId:
	rarity: Rarity
	id: int


class PlayerPetModel:
	def __init__(
		self,
		guid: str,
		pet_id: PetId,
		secondary_stats: SecondaryStats,
	) -> None:
		self.guid = guid
		self.pet_id = pet_id
		self.secondary_stats = secondary_stats
		self.level = 0
		self.experience = 0
		self.is_equipped = False
		self.equip_slot = _EMPTY_EGG_SLOT


class PlayerEggModel:
	def __init__(self, guid: str, rarity: Rarity, seed: int) -> None:
		self.guid = guid
		self.rarity = rarity
		self.seed = seed
		self.timer = TimerModel(start_time=0, end_time=0, duration=0)
		self.is_equipped = False
		self.equip_slot = _EMPTY_EGG_SLOT


class PlayerPvpPetModel:
	def __init__(
		self,
		pet_id: PetId,
		level: int,
		secondary_stats: SecondaryStats,
		equip_slot: int,
		ascension_level: int,
	) -> None:
		self.pet_id = pet_id
		self.level = level
		self.secondary_stats = secondary_stats
		self.equip_slot = equip_slot
		self.ascension_level = ascension_level


class PlayerPetCollectionModel:
	def __init__(self) -> None:
		# IL .ctor: lists, SummonModel, AscensionModel(AscendableType.Pets = 2).
		self.pets: list[PlayerPetModel] = []
		self.eggs: list[PlayerEggModel] = []
		self.unlocked_hatch_slots_count: int = 0
		self.summon_model = SummonModel()
		self.ascension_model = AscensionModel(AscendableType.Pets)

	def ascend(self) -> None:
		self.pets.clear()
		self.eggs.clear()
		self.summon_model.reset()
		self.ascension_model.ascend()

	def create_egg_model(self, rarity: Rarity, seed: int) -> PlayerEggModel:
		# IL: RandomPCG.CreateFromSeed(seed), NextGuid, rarity, seed, timer=0, equip_slot=-1.
		rng = RandomPCG.create_from_seed(seed)
		return PlayerEggModel(rng.next_guid(), rarity, seed)

	def get_equipped_eggs_count(self) -> int:
		return sum(1 for egg in self.eggs if egg.is_equipped)

	def get_equipped_pets(self) -> list[PlayerPetModel]:
		return [pet for pet in self.pets if pet.is_equipped]

	def get_equipped_pets_as_pvp(self) -> list[PlayerPvpPetModel]:
		ascension_level = self.ascension_model.current_level
		return [
			PlayerPvpPetModel(
				pet.pet_id,
				pet.level,
				pet.secondary_stats,
				pet.equip_slot,
				ascension_level,
			)
			for pet in self.get_equipped_pets()
		]

	def try_get_pet_in_slot(self, slot_index: int) -> PlayerPetModel | None:
		for pet in self.pets:
			if pet.is_equipped and pet.equip_slot == slot_index:
				return pet
		return None

	def is_hatch_slot_available(self, slot_index: int) -> bool:
		if slot_index >= self.unlocked_hatch_slots_count:
			return False
		return all(egg.equip_slot != slot_index for egg in self.eggs)

	def try_get_first_free_egg_slot(self) -> tuple[bool, int]:
		for slot in range(self.unlocked_hatch_slots_count):
			if all(egg.equip_slot != slot for egg in self.eggs):
				return True, slot
		return False, _EMPTY_EGG_SLOT

	def try_get_all_free_hatch_slots(self) -> tuple[bool, set[int]]:
		free = {
			slot
			for slot in range(self.unlocked_hatch_slots_count)
			if all(egg.equip_slot != slot for egg in self.eggs)
		}
		return len(free) > 0, free

	def get_empty_pet_slots(self, player: Any) -> list[int]:
		count = self._get_unlocked_pet_slot_count(player)
		return [
			slot
			for slot in range(count)
			if self.try_get_pet_in_slot(slot) is None
		]

	def current_hatch_slot_cost(self, player: Any) -> int:
		unlocked = self.unlocked_hatch_slots_count
		if unlocked == 3:
			return self._pet_base_config(player).egg_hatch_slot_four_cost
		if unlocked == 2:
			return self._pet_base_config(player).egg_hatch_slot_three_cost
		return 100

	@staticmethod
	def _pet_base_config(player: Any) -> Any:
		cfg = getattr(player, "game_config", None)
		if cfg is not None:
			return cfg.pet_base_config
		from ..shared_game_config import get_shared_game_config

		return get_shared_game_config().pet_base_config

	@staticmethod
	def _get_unlocked_pet_slot_count(player: Any) -> int:
		# IL: SharedGameConfigExtensions.GetUnlockedPetSlotCount(player).
		return PlayerPetCollectionModel._pet_base_config(player).pet_slots_count
