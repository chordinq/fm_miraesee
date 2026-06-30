from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Sequence
from ...miraesee_extension import miraesee_extension
from ..enums import AscendableType, Rarity
from ...random_pcg import RandomPCG
from ..stats import SecondaryStats
from ..stats.secondary_stat_helper import SecondaryStatHelper
from .ascension_model import AscensionModel

if TYPE_CHECKING:
	from .player_model import PlayerModel
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
		self.is_locked = False

	def get_resolved_damage(self, player: Any) -> float:
		from ..stats.pet_stats import resolve_pet_primary_stats

		return resolve_pet_primary_stats(player, self)[0]

	def get_resolved_health(self, player: Any) -> float:
		from ..stats.pet_stats import resolve_pet_primary_stats

		return resolve_pet_primary_stats(player, self)[1]

	def get_resolved_stats(self, player: Any) -> tuple[float, float]:
		from ..stats.pet_stats import resolve_pet_primary_stats

		return resolve_pet_primary_stats(player, self)

	def get_display_level(self) -> int:
		return self.level + 1

	def get_experience_required(self, player: Any) -> int:
		from ..stats.pet_stats import get_pet_experience_required, resolve_player_game_config

		return get_pet_experience_required(
			resolve_player_game_config(player), self.pet_id.rarity, self.level
		)

	@staticmethod
	def get_total_level_xp(pet: PlayerPetModel, player: PlayerModel, level: int) -> int:
		from ..stats.experience_helper import _level_info_entries, total_level_xp

		upgrade_config = player.game_config.pet_upgrade_library.get(pet.pet_id.rarity)
		if upgrade_config is None:
			raise ValueError(f"No pet upgrade config for rarity: {pet.pet_id.rarity!r}")
		return total_level_xp(_level_info_entries(upgrade_config), level)

	def get_total_xp(self, player: PlayerModel) -> int:
		return self.get_total_level_xp(self, player, self.level) + self.experience

	@staticmethod
	def calculate_level_and_xp(
		player: PlayerModel,
		pet: PlayerPetModel,
		total_xp: int,
	) -> tuple[int, int]:
		from ..stats.experience_helper import _level_info_entries, calculate_level_and_xp

		upgrade_config = player.game_config.pet_upgrade_library.get(pet.pet_id.rarity)
		if upgrade_config is None:
			raise ValueError(f"No pet upgrade config for rarity: {pet.pet_id.rarity!r}")
		return calculate_level_and_xp(_level_info_entries(upgrade_config), total_xp)


class PlayerEggModel:
	def __init__(self, guid: str, rarity: Rarity, seed: int) -> None:
		self.guid = guid
		self.rarity = rarity
		self.seed = seed
		self.timer: TimerModel | None = None
		self.is_equipped = False
		self.equip_slot = _EMPTY_EGG_SLOT

	def get_xp(self, player: PlayerModel) -> int:
		from ..stats.experience_helper import _level_info_entries, first_level_experience

		upgrade_config = player.game_config.pet_upgrade_library.get(self.rarity)
		if upgrade_config is None:
			raise ValueError(f"No pet upgrade config for rarity: {self.rarity!r}")
		return first_level_experience(_level_info_entries(upgrade_config))


class HatchedPetInfo:
	def __init__(
		self,
		model: PlayerPetModel,
		is_new: bool,
		previous_hatch_slot_id: int,
	) -> None:
		self.pet_id = model.pet_id
		self.is_new = is_new
		self.previous_hatch_slot_id = previous_hatch_slot_id


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
		self.pets: list[PlayerPetModel] = []
		self.eggs: list[PlayerEggModel] = []
		self.unlocked_hatch_slots_count: int = 0
		self.summon_model = SummonModel()
		self.ascension_model = AscensionModel(AscendableType.Pets)

	@miraesee_extension
	def get_pets(self) -> list[PlayerPetModel]:
		return list(self.pets)

	@miraesee_extension
	def get_eggs(self) -> list[PlayerEggModel]:
		return sorted(self.eggs, key=lambda egg: egg.rarity.value, reverse=True)

	def ascend(self) -> None:
		self.pets.clear()
		self.eggs.clear()
		self.summon_model.reset()
		self.ascension_model.ascend()

	def create_egg_model(self, rarity: Rarity, seed: int) -> PlayerEggModel:
		rng = RandomPCG.create_from_seed(seed)
		egg = PlayerEggModel(rng.next_guid(), rarity, seed)
		egg.timer = None
		egg.is_equipped = False
		egg.equip_slot = _EMPTY_EGG_SLOT
		return egg

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
		return player.game_config.pet_base_config

	@staticmethod
	def _get_unlocked_pet_slot_count(player: Any) -> int:
		from ..shared_game_config import get_unlocked_pet_slot_count

		return get_unlocked_pet_slot_count(player)


def create_pet(
	player: PlayerModel,
	pet_id: PetId,
	rng: RandomPCG,
	secondary_stats: SecondaryStats | None = None,
) -> PlayerPetModel:
	game_config = player.game_config
	guid = rng.next_guid()
	ascension_level = player.player_pet_collection_model.ascension_model.current_level
	library = game_config.secondary_stat_pet_unlock_library

	if ascension_level < 1:
		unlock_row = library.get(pet_id.rarity)
	else:
		unlock_row = list(library.values())[-1] if library else None

	if unlock_row is None:
		raise ValueError(f"Missing SecondaryStatPetUnlockLibrary entry for {pet_id.rarity!r}")

	stat_count = int(unlock_row["NumberOfSecondStats"])
	if secondary_stats is None:
		secondary_stats = SecondaryStatHelper.generate_secondary_stats(stat_count, rng)

	return PlayerPetModel(guid, pet_id, secondary_stats)


def create_pet_from_ids(
	player: PlayerModel,
	pet_ids: Sequence[PetId],
	rng: RandomPCG,
	secondary_stats: SecondaryStats | None = None,
) -> PlayerPetModel:
	if not pet_ids:
		raise ValueError("pet_ids must not be empty")
	chosen = rng.choice(list(pet_ids))
	return create_pet(player, chosen, rng, secondary_stats)


def pet_ids_for_rarity(
	pet_library: dict[PetId, dict],
	rarity: Rarity,
) -> list[PetId]:
	return [pet_id for pet_id in pet_library if pet_id.rarity == rarity]
