# models/ForgeModel.py
from core.enums import AscendableType
from core.game_logic.player_model.AscensionModel import AscensionModel

class ForgeModel:
	def __init__(self):
		self.forge_seed = 0
		self.forge_level = 0
		self.forge_count = 0
		self.max_forged_age = 0

		self.ascension_model = AscensionModel(AscendableType.Forge)
		self.pending_items = []