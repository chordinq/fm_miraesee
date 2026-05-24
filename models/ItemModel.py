# models/ItemModel.py
from configs.enums import ItemAge
from configs.enums import ItemType
from models.SecondaryStatsModel import SecondaryStatsModel

class ItemModel:
	def __init__(self, age: ItemAge, type: ItemType, idx: int):
		self.age = age
		self.type = type
		self.idx = idx
		
		self.level = 0
		self.is_new = False
		self.is_newly_forged = False
		
		self.secondary_stats = SecondaryStatsModel()