# models/PetCollectionModel.py
from configs.enums import AscendableType
from models.PetModel import PetModel
from models.EggModel import EggModel
from models.SummonModel import SummonModel
from models.AscensionModel import AscensionModel

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
		combined = []
		for pet in self.pets:
			combined.append({"type": "Pet", "rarity": pet.rarity, "perfection": pet.perfection, "obj": pet})
		if include_eggs:
			for egg in self.eggs:
				combined.append({"type": "Egg", "rarity": egg.rarity, "perfection": 0.0, "obj": egg})
				
		combined.sort(key=lambda x: (x["rarity"].value, x["perfection"]), reverse=True)
		return combined