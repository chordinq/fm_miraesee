# models/EquipmentModel.py
from core.enums import ItemType
from core.game_logic.player_model.ItemModel import ItemModel

class EquipmentModel:
	def __init__(self):
		self.equipped_items = {itype: None for itype in ItemType}
		self.hidden_levels = {itype: {} for itype in ItemType}
		self.round_robin = {itype: {} for itype in ItemType}

	def equip_item(self, item: ItemModel):
		self.equipped_items[item.item_type] = item

	def get_equipped_item(self, item_type: ItemType) -> ItemModel:
		return self.equipped_items.get(item_type)

	def set_hidden_level(self, item_type: ItemType, age: int, level: int):
		self.hidden_levels[item_type][age] = level

	def set_round_robin(self, item_type: ItemType, age: int, indices: list):
		self.round_robin[item_type][age] = indices

	def get_round_robin_indices(self, item_type: ItemType, age: int) -> set[int]:
		return set(self.round_robin.get(item_type, {}).get(age, []))

	def add_round_robin_index(self, item_type: ItemType, age: int, idx: int):
		bucket = self.round_robin[item_type].setdefault(age, [])
		if idx not in bucket:
			bucket.append(idx)

	def reset_round_robin(self, item_type: ItemType, age: int):
		self.round_robin[item_type][age] = []