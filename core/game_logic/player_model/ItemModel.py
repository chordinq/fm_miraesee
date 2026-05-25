# models/ItemModel.py
from core.enums import ItemAge, ItemType
from core.game_logic.player_model.SecondaryStatsModel import SecondaryStatsModel


class ItemModel:
	def __init__(self, age: ItemAge, item_type: ItemType, idx: int):
		self.age = age
		self.item_type = item_type
		self.idx = idx

		self.level = 0
		self.is_new = False
		self.is_newly_forged = False
		self.is_free_forge = False
		self.guid = ""

		self.secondary_stats = SecondaryStatsModel()
