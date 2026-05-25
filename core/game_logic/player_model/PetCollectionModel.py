# models/PetCollectionModel.py
from core.enums import AscendableType
from core.game_logic.player_model.PetModel import PetModel
from core.game_logic.player_model.EggModel import EggModel
from core.game_logic.player_model.SummonModel import SummonModel
from core.game_logic.player_model.AscensionModel import AscensionModel

class PetCollectionModel:
	def __init__(self):
		self.pets = []
		self.eggs = []
		
		self.summon_model = SummonModel()
		self.ascension_model = AscensionModel(AscendableType.Pets)

	def add_pet(self, pet: PetModel):
		self.pets.append(pet)
		self._sort_pets()

	def add_egg(self, egg: EggModel):
		self.eggs.append(egg)
		self._sort_eggs()

	def _sort_pets(self):
		self.pets.sort(
			key=lambda p: (
				not p.is_equipped,
				p.equip_slot,
				-p.rarity.value,
				p.pet_id,
			)
		)

	def _sort_eggs(self):
		self.eggs.sort(
			key=lambda e: (
				not e.is_equipped,
				e.equip_slot,
				-e.rarity.value,
				e.seed,
			)
		)

	def tolist(self, include_eggs=True) -> list:
		combined = []
		for pet in self.pets:
			combined.append({"type": "Pet", "rarity": pet.rarity, "perfection": pet.perfection, "obj": pet})
		if include_eggs:
			for egg in self.eggs:
				combined.append({"type": "Egg", "rarity": egg.rarity, "perfection": 0.0, "obj": egg})
				
		combined.sort(key=lambda x: (x["rarity"].value, x["perfection"]), reverse=True)
		return combined