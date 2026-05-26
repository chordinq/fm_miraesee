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

	def add_egg(self, egg: EggModel):
		self.eggs.append(egg)

	def tolist(self, include_eggs=True) -> list:
		"""Combined pets/eggs: higher rarity first, stable FIFO within tier."""
		combined: list[tuple[int, dict]] = []
		for i, pet in enumerate(self.pets):
			combined.append((i, {"type": "Pet", "rarity": pet.rarity, "perfection": pet.perfection, "obj": pet}))
		if include_eggs:
			base = len(self.pets)
			for j, egg in enumerate(self.eggs):
				combined.append((base + j, {"type": "Egg", "rarity": egg.rarity, "perfection": 0.0, "obj": egg}))
		combined.sort(key=lambda t: (-t[1]["rarity"].value, t[0]))
		return [entry for _, entry in combined]