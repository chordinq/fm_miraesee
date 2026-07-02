from __future__ import annotations

from typing import TYPE_CHECKING, Any

from core.format.format_item import (
	format_secondary_stats,
	format_secondary_stats_collection,
)
from core.game_logic.enums import ItemType, SecondaryStatType, StatType
from core.game_logic.config.shared_game_config import SharedGameConfig
from core.game_logic.stats.stat_helper import StatHelper
from core.game_logic.stats.stat_target import EquipmentStatTarget
from .player_equipment_model import ItemId

if TYPE_CHECKING:
	from .player_model import PlayerModel


class PlayerItemModel:
	def __init__(
		self,
		guid: str,
		item_id: ItemId,
		level: int = 0,
		*,
		secondary_stats=None,
	) -> None:
		from core.game_logic.stats import SecondaryStats

		self.guid = guid
		self.item_id = item_id
		self.level = level
		self.is_new = False
		self.is_newly_forged = False
		self.secondary_stats = secondary_stats or SecondaryStats()

	@property
	def age(self):
		return self.item_id.Age

	@property
	def item_type(self) -> ItemType:
		return self.item_id.Type


def is_ranged_weapon(item_id: ItemId, game_config: Any) -> bool:
	"""IL: PlayerItemModelExtensions.IsRangedWeapon(ItemId)."""
	if item_id.Type != ItemType.Weapon:
		return False
	weapons = getattr(game_config, "weapons", None)
	if weapons is None:
		return False
	weapon_info = weapons.get(item_id)
	if weapon_info is None:
		return False
	return bool(weapon_info.get("IsRanged", False))


def get_sell_value(player: PlayerModel, item_to_sell: PlayerItemModel) -> int:
	"""IL: SellValueHelper.GetSellValue."""
	game_config = player.game_config
	balancing = game_config.item_balancing_config
	scaled = balancing.level_scaling_base ** item_to_sell.level
	base_value = balancing.sell_base_price * scaled
	target = EquipmentStatTarget(item_to_sell.item_id.Type)
	value = StatHelper.calculate_value(
		player,
		StatType.SellPrice,
		target,
		base_value,
	)
	return round(value)


__all__ = [
	"PlayerItemModel",
	"is_ranged_weapon",
	"get_sell_value",
	"format_secondary_stats",
	"format_secondary_stats_collection",
]
