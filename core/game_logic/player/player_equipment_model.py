from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import uuid4
from ..enums import ItemAge, ItemType, StatType
from ..stats import SecondaryStats
from ..stats.stat_helper import StatHelper
from ..stats.stat_target import EquipmentStatTarget

if TYPE_CHECKING:
	from .player_model import PlayerModel

@dataclass(frozen=True)
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

_SLOT_FIELDS = (
	"helmet",
	"armour",
	"gloves",
	"necklace",
	"ring",
	"weapon",
	"shoes",
	"belt",
)


class PlayerEquipmentModel:
	def __init__(
		self,
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
		self.hidden_item_levels: dict[ItemType, dict[int, int]] = {}
		self.item_round_robin: dict[ItemType, dict[int, list[int]]] = {}

	def set_item_at_slot(self, slot_index: int, item: ItemModel | None) -> None:
		if slot_index < 0 or slot_index >= len(_SLOT_FIELDS):
			return
		setattr(self, _SLOT_FIELDS[slot_index], item)

	def set_hidden_level(self, item_type: ItemType, age: int, level: int) -> None:
		self.hidden_item_levels.setdefault(item_type, {})[age] = level

	def set_round_robin(self, item_type: ItemType, age: int, indices: list[int]) -> None:
		self.item_round_robin.setdefault(item_type, {})[age] = list(indices)

	def get_round_robin_list(self, item_type: ItemType, age: int) -> list[int]:
		by_age = self.item_round_robin.get(item_type)
		if by_age is None:
			return []
		return by_age.get(age, [])

	def get_hidden_level(self, item_type: ItemType, age: int) -> int:
		by_age = self.hidden_item_levels.get(item_type)
		if by_age is None:
			return 0
		return by_age.get(age, 0)

	def get_items(self) -> dict[ItemType, ItemModel]:
		items: dict[ItemType, ItemModel] = {}
		for slot_name in _SLOT_FIELDS:
			item = getattr(self, slot_name)
			if item is not None:
				items[item.item_id.Type] = item
		return items

	def try_reset_round_robin(
		self,
		possible_items: list[ItemId],
		item_type: ItemType,
		age: int,
	) -> None:
		by_type = self.item_round_robin.get(item_type)
		if by_type is None or age not in by_type:
			return
		rolled = by_type[age]
		if len(possible_items) <= len(rolled):
			rolled.clear()

	def add_or_reset_round_robin(
		self,
		possible_items: list[ItemId],
		item: ItemId,
	) -> None:
		by_type = self.item_round_robin.setdefault(item.Type, {})
		rolled = by_type.setdefault(int(item.Age), [])
		if len(rolled) < len(possible_items) and item.Idx not in rolled:
			rolled.append(item.Idx)
		else:
			rolled.clear()

	def increment_hidden_item_level(self, player: PlayerModel, item: ItemId) -> None:
		game_config = player.game_config
		base_max = game_config.item_balancing_config.item_base_max_level
		target = EquipmentStatTarget(item.Type)
		calculated = StatHelper.calculate_value(
			player,
			StatType.MaxLevel,
			target,
			base_max,
		)

		bracket_level = 0
		library = game_config.item_level_brackets_library
		for index in sorted(library.keys()):
			bracket = library[index]
			upper = float(bracket.get("UpperRange", 0))
			if upper >= calculated:
				bracket_level = int(bracket.get("Level", 0))
				break

		by_type = self.hidden_item_levels.setdefault(item.Type, {})
		current = by_type.get(int(item.Age), 0)
		if current < bracket_level:
			by_type[int(item.Age)] = current + 1

	def ascend(self) -> None:
		self.helmet = None
		self.armour = None
		self.gloves = None
		self.necklace = None
		self.ring = None
		self.shoes = None
		self.belt = None
		self.weapon = self.default_weapon_model
		self.hidden_item_levels.clear()
		self.item_round_robin.clear()

	@property
	def default_weapon_model(self) -> ItemModel | None:
		return self.weapon
