"""Python bridge for TMPText — core/format strings only (no loc in QML)."""
from __future__ import annotations

from PySide6.QtCore import QObject, Slot

from config import string_literal
from core.format.format_techtree import (
	format_tech_tree_active_research_suffix as _format_tech_tree_active_research_suffix,
	format_tech_tree_complete_suffix as _format_tech_tree_complete_suffix,
	parenthesized_text as _parenthesized_text,
)
from core.format import (
	format_level,
	format_level_plus_one,
	format_long,
	format_power,
	format_percentage,
	format_stat,
	get_localized,
	get_translation,
)
from core.format.number_format import maxed_progress_label as _maxed_progress_label
from core.game_logic.enums import CurrencyType
from controllers.common.ui_format import format_ui_integer
from ui.utils.localizer import bracketed_title

from . import inline_sprites

# IL: StringLiteral_25577 → "{0} x{1}" (summon button title)
_SUMMON_TITLE_FORMAT = string_literal(25577)
# IL: StringLiteral_25321 → "x{0}" (bulk summon count toggle)
_BULK_COUNT_FORMAT = string_literal(25321)


class TmpTextBridge(QObject):
	@Slot(str, str, result=str)
	def localized_text(self, loc_id: str, language: str) -> str:
		return get_localized(loc_id, table="General", language=language)

	@Slot(str, str, str, result=str)
	def localized_text_table(self, loc_id: str, language: str, table: str) -> str:
		return get_localized(loc_id, table=table, language=language)

	@Slot(str, str, str, "QVariantList", result=str)
	def localized_text_with_args(
		self,
		loc_id: str,
		language: str,
		table: str,
		args: list,
	) -> str:
		py_args = list(args) if args is not None else []
		return get_localized(
			loc_id,
			table=table,
			language=language,
			args=py_args,
		)

	@Slot(str, result=str)
	def skip_button_title(self, language: str) -> str:
		return get_translation("Skip", table="General", language=language)

	@Slot(str, int, result=str)
	def summon_button_title(self, language: str, summon_count: int) -> str:
		word = get_translation("Summon", table="General", language=language)
		count_text = format_ui_integer(summon_count)
		return _SUMMON_TITLE_FORMAT.format(word, count_text)

	@Slot(str, int, result=str)
	def skill_summon_title(self, language: str, summon_count: int) -> str:
		return self.summon_button_title(language, summon_count)

	@Slot(int, result=str)
	def bulk_summon_count_text(self, count: int) -> str:
		return _BULK_COUNT_FORMAT.format(format_ui_integer(count))

	@Slot("QVariantList", str, result=str)
	def join_loc_segments(self, segments: list, language: str) -> str:
		parts: list[str] = []
		for segment in segments or []:
			if not isinstance(segment, dict):
				continue
			loc_id = str(segment.get("locId", ""))
			table = str(segment.get("locTable", "General"))
			text = get_localized(loc_id, table=table, language=language)
			if text:
				parts.append(text)
		return " ".join(parts)

	@Slot(str, str, str, str, str, result=str)
	def bracketed_title_text(
		self,
		rarity_loc_id: str,
		rarity_table: str,
		name_loc_id: str,
		name_table: str,
		language: str,
	) -> str:
		return bracketed_title(
			rarity_loc_id,
			rarity_table,
			name_loc_id,
			name_table,
			language=language,
		)

	@Slot(int, result=str)
	def format_integer_text(self, value: int) -> str:
		return format_ui_integer(value)

	@Slot(int, result=str)
	def currency_icon_source(self, currency_type: int) -> str:
		return inline_sprites.currency_icon_source(CurrencyType(currency_type))

	@Slot(int, int, result=str)
	def format_currency_value_text(self, amount: int, currency_type: int) -> str:
		return inline_sprites.format_currency_value_text(amount, CurrencyType(currency_type))

	@Slot(int, int, int, result=str)
	def format_currency_line_text(
		self,
		amount: int,
		currency_type: int,
		show_icon: int = 1,
	) -> str:
		_ = show_icon
		return inline_sprites.format_currency_value_text(amount, CurrencyType(currency_type))

	@Slot(int, str, int, result=str)
	def format_level_text(
		self,
		level: int,
		language: str,
		abbreviated_tag: int,
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
		language: str,
		abbreviated_tag: int,
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
	def format_stat_text(self, value: float, digits: int) -> str:
		return format_stat(value, digits)

	@Slot(float, result=str)
	def format_percentage_text(self, value: float) -> str:
		return format_percentage(value)

	@Slot(str, result=str)
	def maxed_progress_label(self, language: str) -> str:
		return _maxed_progress_label(language=language)

	@Slot(str, result=str)
	def parenthesized_text(self, inner: str) -> str:
		return _parenthesized_text(inner)

	@Slot(str, result=str)
	def tech_tree_complete_suffix(self, language: str) -> str:
		return _format_tech_tree_complete_suffix(language=language)

	@Slot(str, result=str)
	def tech_tree_active_research_suffix(self, timer_text: str) -> str:
		return _format_tech_tree_active_research_suffix(timer_text)

	@Slot(int, result=str)
	def format_power_text(self, value: int) -> str:
		return format_power(value)
