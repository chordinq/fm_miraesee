from __future__ import annotations

from typing import TYPE_CHECKING

from .enums import StatType
from .stats.stat_helper import StatHelper
from .stats.stat_target import EquipmentStatTarget

if TYPE_CHECKING:
	from .player.player_item_model import PlayerItemModel
	from .player.player_model import PlayerModel


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
