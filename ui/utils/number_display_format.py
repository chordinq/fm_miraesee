from __future__ import annotations

from core.game_logic.enums import CurrencyType
from core.game_logic.fd6_math import format_fd6_raw
from core.game_logic.number_format import format, format_currency, format_long
from ui_settings import game_number_formatting_enabled


def format_ui_integer(value: int | float) -> str:
	if not game_number_formatting_enabled():
		return format_fd6_raw(float(value))
	if isinstance(value, int):
		return format_long(value)
	return format(float(value))


def format_ui_currency(
	amount: int | float,
	currency_type: CurrencyType,
	*,
	icon_prefix: str = "",
) -> str:
	if not game_number_formatting_enabled():
		text = format_fd6_raw(float(amount))
	elif isinstance(amount, int):
		text = format_currency(amount, currency_type, show_icon=False)
	else:
		text = format_currency(float(amount), currency_type, show_icon=False)
	if icon_prefix:
		return icon_prefix + text
	return text
