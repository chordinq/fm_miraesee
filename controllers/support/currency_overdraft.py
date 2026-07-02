from __future__ import annotations

from typing import TYPE_CHECKING

from core.game_logic.enums import CurrencyType
from core.game_logic.player.player_currency_model import can_afford

if TYPE_CHECKING:
	from core.game_logic.player.player_model import PlayerModel


def can_afford_currency_for_ui(
	player: PlayerModel,
	currency_type: CurrencyType,
	amount: int,
) -> bool:
	if amount < 1:
		return True
	affordable, _ = can_afford(player, currency_type, amount)
	return affordable


def spend_currency_for_ui(
	player: PlayerModel,
	currency_type: CurrencyType,
	amount: int,
	sink_name: str,
) -> bool:
	if amount < 1:
		return True
	affordable, spend_context = can_afford(player, currency_type, amount)
	if not affordable or spend_context is None:
		return False
	spend_context.spend(sink_name)
	return True
