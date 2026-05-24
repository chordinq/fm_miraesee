# models/ForgeModel.py
from configs.enums import AscendableType
from models.AscensionModel import AscensionModel

class ForgeModel:
	def __init__(self):
		self.forge_seed = 0
		self.forge_level = 0
		self.forge_count = 0
		
		self.ascension_model = AscensionModel(AscendableType.Forge)
		
		self.free_forge_chance = 0.0