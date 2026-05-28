# models/PetCollectionModel.py
from core.enums import AscendableType
from core.game_logic.player_model.PetModel import PetModel
from core.game_logic.player_model.EggModel import EggModel
from core.game_logic.player_model.SummonModel import SummonModel
from core.game_logic.player_model.AscensionModel import AscensionModel


def _pet_sort_key(index: int, pet: PetModel) -> tuple:
	"""Equipped → Rarity (desc) → Lv (desc) → FIFO."""
	return (not pet.is_equipped, -pet.rarity.value, -pet.level, index)


def _egg_sort_key(index: int, egg: EggModel) -> tuple:
	"""Rarity (desc) → FIFO. Eggs ignore equipped for ordering."""
	return (-egg.rarity.value, index)


HATCH_SLOT_COUNT = 4


def _in_hatch_slot(egg: EggModel) -> bool:
	"""In-game hatch incubator: equipped flag + slot index 0..3."""
	return egg.is_equipped and 0 <= egg.equip_slot < HATCH_SLOT_COUNT


class PetCollectionModel:
	def __init__(self):
		self.pets = []
		self.eggs = []

		self.summon_model = SummonModel()
		self.ascension_model = AscensionModel(AscendableType.Pets)

	def add_pet(self, pet: PetModel):
		self.pets.append(pet)

	def add_egg(self, egg: EggModel):
		self.eggs.append(egg)

	def hatch_slots(self) -> list[EggModel | None]:
		slots: list[EggModel | None] = [None] * HATCH_SLOT_COUNT
		for egg in self.eggs:
			if _in_hatch_slot(egg):
				slots[egg.equip_slot] = egg
		return slots

	def tolist(self, include_eggs=True) -> list:
		result: list[dict] = []

		for i, pet in sorted(enumerate(self.pets), key=lambda t: _pet_sort_key(t[0], t[1])):
			result.append(
				{
					"type": "Pet",
					"rarity": pet.rarity,
					"perfection": pet.perfection,
					"obj": pet,
				}
			)

		if include_eggs:
			inventory = [e for e in self.eggs if not _in_hatch_slot(e)]
			for _i, egg in sorted(enumerate(inventory), key=lambda t: _egg_sort_key(t[0], t[1])):
				result.append(
					{
						"type": "Egg",
						"rarity": egg.rarity,
						"perfection": 0.0,
						"obj": egg,
					}
				)

		return result
