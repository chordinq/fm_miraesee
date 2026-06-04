from ..enums import ItemAge, ItemType
from ..stats import SecondaryStats
from dataclasses import dataclass
from uuid import uuid4

@dataclass
class ItemId:
	Age: ItemAge
	Type: ItemType
	Idx: int

class ItemModel:
	def __init__(self, age: ItemAge, item_type: ItemType, idx: int, level: int = 0):
		self.guid = str(uuid4())
		self.item_id = ItemId(age, item_type, idx)
		self.level = level
		self.is_new = False
		self.is_newly_forged = False
		self.secondary_stats = SecondaryStats()

class PlayerEquipmentModel:
	def __init__(self,
		helmet: ItemModel | None = None,
		armour: ItemModel | None = None,
		gloves: ItemModel | None = None,
		necklace: ItemModel | None = None,
		ring: ItemModel | None = None,
		weapon: ItemModel | None = None,
		shoes: ItemModel | None = None,
		belt: ItemModel | None = None,
	):
		self.helmet = helmet
		self.armour = armour
		self.gloves = gloves
		self.necklace = necklace
		self.ring = ring
		self.weapon = weapon
		self.shoes = shoes
		self.belt = belt
