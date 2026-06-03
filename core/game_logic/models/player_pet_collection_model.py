from __future__ import annotations
from dataclasses import dataclass
from uuid import uuid4
from ..enums import Rarity, PetBalancingType, SummonKind, AscendableType
from ..secondary_stats import SecondaryStats
from .summon_model import SummonModel
from .ascension_model import AscensionModel
from .timer_model import TimerModel
from config import PET_LIBRARY, EGG_LIBRARY, PET_BALANCING_LIBRARY, PET_UPGRADE_LIBRARY

@dataclass(frozen=True)
class PetId:
    rarity: Rarity
    id: int

class PlayerPetModel:
	def __init__(self,
		pet_id: PetId,
		level: int = 0,
		experience: int = 0,
		is_equipped: bool = False,
		equip_slot: int = 0,
		secondary_stats: SecondaryStats = SecondaryStats()
	) -> None:
		self.guid = str(uuid4())
		self.pet_id = pet_id
		self.level = level
		self.experience = experience
		self.is_equipped = is_equipped
		self.equip_slot = equip_slot
		self.secondary_stats = secondary_stats

class PlayerEggModel:
	def __init__(self, rarity: Rarity, seed: int):
		self.guid = str(uuid4())
		self.rarity = rarity
		self.timer = TimerModel(start_time=0, end_time=0, duration=0)
		self.seed = seed
		self.is_equipped = False
		self.equip_slot = 0

class PlayerPetCollectionModel:
	def __init__(self):
		self.player_pet_models: list[PlayerPetModel] = []
		self.player_egg_models: list[PlayerEggModel] = []
		self.unlocked_hatch_slots_count: int = 0
		self.summon_model = SummonModel()
		self.ascension_model = AscensionModel(AscendableType.Pets)

	def get_equipped_eggs_count(self) -> int:
		return sum(1 for egg in self.player_egg_models if egg.is_equipped)

	def get_empty_pet_slots(self) -> list[int]:
		return [i for i in range(self.unlocked_hatch_slots_count) if i not in [pet.equip_slot for pet in self.player_pet_models]]
