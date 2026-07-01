from __future__ import annotations

from core.game_logic.enums import CurrencyType
from core.metaplaymath.fd6 import format_fd6_raw
from core.format.number_format import format_currency_value
from core.format.numbers import format, format_long
from ui.utils.ui_settings import game_number_formatting_enabled


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
		text = format_currency_value(amount)
	else:
		text = format_currency_value(float(amount))
	if icon_prefix:
		return icon_prefix + text
	return text
