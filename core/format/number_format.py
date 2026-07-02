"""IL: NumberFormat (TypeDefIndex 7727)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from . import localizer_base as localization
from . import numbers
from config import string_literal

if TYPE_CHECKING:
	pass

_LEVEL_ABBREV_LOC_KEY = string_literal(10404)
_LEVEL_FULL_LOC_KEY = string_literal(10206)
_LEVEL_FORMAT_PATTERN = string_literal(25578)
_PERCENT_SUFFIX = string_literal(827)
# IL StringLiteral_25629 — SkillProgressUiView, TechTreeNodeUiView, SummonUpgradeStatusUiView
_PROGRESS_PAIR_FORMAT = string_literal(25629)
# IL StringLiteral_10561 — TechTreeNodeUiView max-level pill
_MAX_PROGRESS_LABEL = string_literal(10561)
# IL StringLiteral_10635 — GetTranslation key "Maxed" (SummonUpgradeStatusUiView, SkillProgress)
_MAXED_PROGRESS_LOC_KEY = string_literal(10635)


def format_currency_value(amount: int | float) -> str:
	"""Numeric portion of NumberFormat.FormatCurrency (sprite via inline_sprites.format_currency)."""
	if isinstance(amount, int):
		return numbers.format_long(amount)
	if isinstance(amount, float):
		return numbers.format_multiplier(amount, 2)
	return numbers.format_long(int(amount))


def format_damage(number: float) -> str:
	"""IL: NumberFormat.FormatDamage(float number)."""
	return numbers.format(number, numbers.round_down)


def format_multiplier(number: float, decimals: int = 2) -> str:
	"""IL: NumberFormat.FormatMultiplier(F64/FD6 number, int decimals)."""
	return numbers.format_multiplier(number, decimals)


def format_power(number: int | float) -> str:
	"""IL: NumberFormat.FormatPower(long/F64/FD6/UInt128) — zero → empty string."""
	if number == 0:
		return ""
	text = numbers.format(float(number))
	return text if text else ""


def format_percentage(number: float) -> str:
	"""IL: NumberFormat.FormatPercentage(F64/FD6 number)."""
	text = numbers.format_multiplier_3_significant_digits(number * 100.0)
	return f"{text}{_PERCENT_SUFFIX}"


def format_drop_chance_percentage(
	number: float,
	digits: int = 2,
	rounding_mode: object | None = None,
) -> str:
	"""IL: NumberFormat.FormatDropChancePercentage(F64/FD6, digits, RoundingMode?)."""
	text = numbers.format_multiplier_fixed(
		number * 100.0, digits, rounding_mode
	)
	return f"{text}{_PERCENT_SUFFIX}"


def format_stat(number: float, digits: int = 0) -> str:
	"""IL: NumberFormat.FormatStat(F64/FD6 number, int digits = 0)."""
	if digits == 0:
		return numbers.format(number)
	return numbers.format_multiplier_1_significant_digits(number)


def format_level(
	level: int,
	*,
	abbreviated_tag: bool = True,
	language: str = "en",
) -> str:
	"""IL: NumberFormat.FormatLevel(int level, bool abbreviatedTag)."""
	loc_key = _LEVEL_ABBREV_LOC_KEY if abbreviated_tag else _LEVEL_FULL_LOC_KEY
	tag = localization.get_translation(loc_key, language=language)
	return _LEVEL_FORMAT_PATTERN.format(tag, level)


def format_level_plus_one(
	level: int,
	*,
	abbreviated_tag: bool = True,
	language: str = "en",
) -> str:
	"""IL: NumberFormat.FormatLevelPlusOne(int level, bool abbreviatedTag)."""
	return format_level(level + 1, abbreviated_tag=abbreviated_tag, language=language)


def format_progress_pair(
	current: int | float,
	total: int | float,
	*,
	format_value=None,
) -> str:
	"""IL: String.Format(StringLiteral_25629, Numbers.Format(n), Numbers.Format(m))."""
	fmt = format_value or (lambda value: numbers.format_long(int(value)))
	return _PROGRESS_PAIR_FORMAT.format(fmt(current), fmt(total))


def max_progress_label() -> str:
	"""IL: StringLiteral_10561 shown on max-level tech tree node icon."""
	return _MAX_PROGRESS_LABEL


def maxed_progress_label(*, language: str | None = None) -> str:
	"""IL: LocalizerBase.GetTranslation(StringLiteral_10635) → key ``Maxed``."""
	return localization.get_translation(
		_MAXED_PROGRESS_LOC_KEY,
		table="General",
		language=language,
	)
