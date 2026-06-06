from __future__ import annotations
from ..enums import ItemAge, ItemType
from ..stats import SecondaryStats
from .player_equipment_model import ItemId


class PlayerItemModel:
	def __init__(
		self,
		guid: str,
		item_id: ItemId,
		level: int = 0,
		*,
		secondary_stats: SecondaryStats | None = None,
	) -> None:
		self.guid = guid
		self.item_id = item_id
		self.level = level
		self.is_new = False
		self.is_newly_forged = False
		self.secondary_stats = secondary_stats or SecondaryStats()

	@property
	def age(self) -> ItemAge:
		return self.item_id.Age

	@property
	def item_type(self) -> ItemType:
		return self.item_id.Type
