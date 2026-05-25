# models/PetModel.py
from core.enums import Rarity
from core.game_logic.player_model.SecondaryStatsModel import SecondaryStatsModel

class PetModel:
	def __init__(self, pet_id: int, rarity: Rarity):
		self.pet_id = pet_id
		self.rarity = rarity
		
		self.level = 0
		self.experience = 0
		self.is_equipped = False
		self.equip_slot = 0
		
		self.secondary_stats = SecondaryStatsModel()