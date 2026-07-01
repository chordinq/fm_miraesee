"""IL: NumberFormat.FormatCurrency — numeric text only (icon via ui/TMPText)."""
from __future__ import annotations

from core.game_logic.enums import CurrencyType

from .number_format import format_currency_value


def format_currency(
	amount: int | float,
	currency_type: CurrencyType,
	*,
	show_icon: bool = True,
) -> str:
	"""IL: NumberFormat.FormatCurrency — value string; icon is UI concern."""
	_ = currency_type, show_icon
	return format_currency_value(amount)
