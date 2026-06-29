from __future__ import annotations

from typing import TYPE_CHECKING

from core.game_logic.enums import CurrencyType
from core.game_logic.player.player_currency_model import can_afford
from ui.utils.ui_settings import allow_negative_currency_enabled

if TYPE_CHECKING:
	from core.game_logic.player.player_model import PlayerModel


def can_afford_currency_for_ui(
	player: PlayerModel,
	currency_type: CurrencyType,
	amount: int,
) -> bool:
	if amount < 1:
		return True
	if allow_negative_currency_enabled():
		return True
	return player.player_currency_model.can_afford(currency_type, amount)


def spend_currency_for_ui(
	player: PlayerModel,
	currency_type: CurrencyType,
	amount: int,
	sink_name: str,
) -> bool:
	if amount < 1:
		return True
	if allow_negative_currency_enabled():
		player.player_currency_model.add_or_subtract(currency_type, -amount)
		return True
	affordable, spend_context = can_afford(player, currency_type, amount)
	if not affordable or spend_context is None:
		return False
	spend_context.spend(sink_name)
	return True
