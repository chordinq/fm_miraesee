# models/MountModel.py
from core.enums import Rarity
from core.game_logic.player_model.SecondaryStatsModel import SecondaryStatsModel

class MountModel:
	def __init__(self, mount_id: int, rarity: Rarity):
		self.mount_id = mount_id
		self.rarity = rarity
		
		self.level = 0
		self.experience = 0
		self.is_equipped = False
		
		self.secondary_stats = SecondaryStatsModel()