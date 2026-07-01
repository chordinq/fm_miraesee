"""Python bridge for TMPText."""
from __future__ import annotations

from PySide6.QtCore import QObject, Slot

from core.format import (
	format_level,
	format_level_plus_one,
	format_long,
	format_power,
	format_percentage,
	format_stat,
)
from core.game_logic.enums import CurrencyType

from . import inline_sprites


class TmpTextBridge(QObject):
	@Slot(int, result=str)
	def currency_icon_source(self, currency_type: int) -> str:
		return inline_sprites.currency_icon_source(CurrencyType(currency_type))

	@Slot(int, int, result=str)
	def format_currency_value_text(self, amount: int, currency_type: int) -> str:
		return inline_sprites.format_currency_value_text(amount, CurrencyType(currency_type))

	@Slot(int, str, int, result=str)
	def format_level_text(
		self,
		level: int,
		language: str = "en",
		abbreviated_tag: int = 1,
	) -> str:
		return format_level(
			level,
			abbreviated_tag=bool(abbreviated_tag),
			language=language,
		)

	@Slot(int, str, int, result=str)
	def format_level_plus_one_text(
		self,
		level: int,
		language: str = "en",
		abbreviated_tag: int = 1,
	) -> str:
		return format_level_plus_one(
			level,
			abbreviated_tag=bool(abbreviated_tag),
			language=language,
		)

	@Slot(int, result=str)
	def format_long_text(self, amount: int) -> str:
		return format_long(amount)

	@Slot(float, int, result=str)
	def format_stat_text(self, value: float, digits: int = 0) -> str:
		return format_stat(value, digits)

	@Slot(float, result=str)
	def format_percentage_text(self, value: float) -> str:
		return format_percentage(value)

	@Slot(int, result=str)
	def format_power_text(self, value: int) -> str:
		return format_power(value)
