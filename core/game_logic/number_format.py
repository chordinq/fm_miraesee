from __future__ import annotations

import math
from collections.abc import Callable
from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from .enums import CurrencyType

_SUFFIXES = ("K", "M", "B", "T", "Q")

_LEVEL_ABBREV_LOC_ID = "25799296414314496"


def round_down(value: float) -> int:
	"""IL: Numbers.RoundDown(double value)"""
	return int(math.floor(value))


def round_up(value: float) -> int:
	"""IL: Numbers.RoundUp(double value)"""
	return int(math.ceil(value))


def round_digits(value: float, digits: int) -> float:
	"""IL: Numbers.RoundDigits(double value, int digits) → Math.Round(..., ToEven)"""
	return round(value, digits)


def floor_double(value: float, digits: int) -> float:
	"""IL: Numbers.FloorDouble — Truncate(value × 10^(digits+1)) / 10^(digits+1)."""
	power = 10.0 ** (digits + 1)
	return math.trunc(power * value) / power


def _log10_magnitude(value: float) -> int:
	if value <= 0.0 or not math.isfinite(value):
		return -2147483648
	return int(math.floor(math.log10(value)))


def _format_double_us(value: float) -> str:
	if value == int(value) and abs(value) < 1e15:
		return str(int(value))
	return f"{value:.10f}".rstrip("0").rstrip(".")


def _string_without_trailing_zeroes(value: float, digits: int) -> str:
	"""IL: g__GetStringWithoutTrailingZeroes — Double.ToString(F{digits}) then TrimEnd."""
	if digits <= 0:
		return str(int(math.trunc(value)))
	quantizer = Decimal(f"0.{'0' * (digits - 1)}1")
	rounded = Decimal(str(value)).quantize(quantizer, rounding=ROUND_HALF_UP)
	text = f"{rounded:f}"
	if "." not in text:
		return text
	return text.rstrip("0").rstrip(".")


def _format_with_suffix_multiplier_1(value: float) -> str:
	"""IL: FormatMultiplier1SignificantDigits g__FormatWithSuffix|11_1"""
	sign = "-" if value < 0 else ""
	abs_value = abs(value)
	log_magnitude = _log10_magnitude(abs_value)
	if not math.isfinite(abs_value) or log_magnitude < 0:
		return sign + format_multiplier_1_significant_digits(abs_value)
	suffix_index = log_magnitude // 3
	divisor = 10.0 ** (suffix_index * 3)
	unit = format_multiplier_1_significant_digits(abs_value / divisor)
	if suffix_index < 1 or suffix_index > len(_SUFFIXES):
		return sign + unit
	return sign + unit + _SUFFIXES[suffix_index - 1]


def _format_with_suffix_multiplier_3(value: float) -> str:
	"""IL: FormatMultiplier3SignificantDigits g__FormatWithSuffix|12_1"""
	sign = "-" if value < 0 else ""
	abs_value = abs(value)
	log_magnitude = _log10_magnitude(abs_value)
	if not math.isfinite(abs_value) or log_magnitude < 0:
		return sign + format_multiplier_3_significant_digits(abs_value)
	suffix_index = log_magnitude // 3
	divisor = 10.0 ** (suffix_index * 3)
	unit = format_multiplier_3_significant_digits(abs_value / divisor)
	if suffix_index < 1 or suffix_index > len(_SUFFIXES):
		return sign + unit
	return sign + unit + _SUFFIXES[suffix_index - 1]


def _format_scaled_with_round(
	value: float,
	round_fn: Callable[[float], int],
) -> str:
	"""IL: Numbers.Format(double, round_fn, formatString) suffix branch."""
	abs_value = abs(value)
	sign = "-" if value < 0 else ""
	log_magnitude = _log10_magnitude(abs_value)

	suffix_index = log_magnitude // 3
	divisor = 10.0 ** (suffix_index * 3)
	scale = 10.0 ** ((suffix_index * 3 - log_magnitude) + 2)
	rounded = round_fn((abs_value / divisor) * scale)
	display = rounded / scale
	if display >= 1000.0:
		display /= 1000.0
		suffix_index += 1

	if suffix_index < 1 or suffix_index > len(_SUFFIXES):
		return f"{sign}{round_fn(abs_value)}"

	text = _format_double_us(display)
	return f"{sign}{text}{_SUFFIXES[suffix_index - 1]}"


def format(
	value: float,
	round_fn: Callable[[float], int] | None = None,
	show_below_one: bool = False,
) -> str:
	"""IL: Numbers.Format overloads.

	Format(value) → Format(value, RoundDown, showBelowOne: false)
	Format(value, round_fn, showBelowOne) → small-value branches + suffix path
	"""
	round_callback = round_down if round_fn is None else round_fn
	abs_value = abs(value)
	sign = "-" if value < 0 else ""

	if abs_value == 0.0:
		return "0"

	log_magnitude = _log10_magnitude(abs_value)
	if math.isfinite(abs_value) and log_magnitude > 2:
		return _format_scaled_with_round(value, round_callback)

	if abs_value >= 1.0 or not show_below_one:
		if abs_value >= 10.0 or not show_below_one:
			return f"{sign}{round_callback(abs_value)}"
		rounded = round_digits(abs_value, 3)
		return f"{sign}{_format_double_us(rounded)}"

	rounded = round_digits(abs_value, 3)
	return f"{sign}{_format_double_us(rounded)}"


def format_long(number: int) -> str:
	"""IL: Numbers.FormatLong(long number)"""
	return format(float(number))


def format_multiplier(value: float, decimals: int = 2) -> str:
	"""IL: Numbers.FormatMultiplier(double value, int decimals)"""
	scaled = round(value, decimals)
	text = f"{scaled:.{decimals}f}".rstrip("0").rstrip(".")
	return text


def format_multiplier_fixed(
	value: float,
	digits: int = 2,
	rounding_mode: object | None = None,
) -> str:
	"""IL: Numbers.FormatMultiplierFixed(double value, int digits, RoundingMode?)"""
	del rounding_mode
	scaled = round(value, digits)
	text = f"{scaled:.{digits}f}".rstrip("0").rstrip(".")
	return text


def format_multiplier_1_significant_digits(value: float) -> str:
	"""IL: Numbers.FormatMultiplier1SignificantDigits(double value)"""
	if value >= 1000.0:
		return _format_with_suffix_multiplier_1(value)
	if value >= 100.0:
		floored = floor_double(value, 0)
		return _string_without_trailing_zeroes(floored, 0)
	floored = floor_double(value, 1)
	return _string_without_trailing_zeroes(floored, 1)


def format_multiplier_3_significant_digits(value: float) -> str:
	"""IL: Numbers.FormatMultiplier3SignificantDigits(double value)"""
	if value >= 1000.0:
		return _format_with_suffix_multiplier_3(value)
	if value >= 100.0:
		floored = floor_double(value, 0)
		return _string_without_trailing_zeroes(floored, 0)
	if value >= 0.01:
		if value >= 10.0:
			floored = floor_double(value, 1)
			return _string_without_trailing_zeroes(floored, 1)
		floored = floor_double(value, 2)
		return _string_without_trailing_zeroes(floored, 2)
	floored = floor_double(value, 3)
	return _string_without_trailing_zeroes(floored, 3)


def format_currency(
	amount: int | float,
	currency_type: CurrencyType,
	*,
	show_icon: bool = True,
	icon_prefix: str = "",
) -> str:
	"""IL: NumberFormat.FormatCurrency(long/double/int, CurrencyType, bool showIcon)

	InlineSprites.InlineIcon(CurrencyType) is UI-only; pass icon_prefix from presentation layer.
	"""
	del currency_type
	if isinstance(amount, int):
		text = format_long(amount)
	else:
		text = format_multiplier(float(amount), 2)
	if show_icon and icon_prefix:
		return icon_prefix + text
	return text


def format_damage(value: float) -> str:
	"""IL: NumberFormat.FormatDamage(float number)"""
	return format(value, round_down)


def format_drop_chance_percentage(
	value: float,
	digits: int = 2,
	rounding_mode: object | None = None,
) -> str:
	"""IL: NumberFormat.FormatDropChancePercentage(F64/FD6, digits, RoundingMode?)"""
	text = format_multiplier_fixed(value * 100.0, digits, rounding_mode)
	return f"{text}%"


def format_level(
	level: int,
	*,
	abbreviated_tag: bool = True,
	level_label: str | None = None,
) -> str:
	"""IL: NumberFormat.FormatLevel(int level, bool abbreviatedTag)

	UI uses General loc {_LEVEL_ABBREV_LOC_ID} (\"Lv.\") + level separately (see LevelText.qml).
	Pass level_label when resolved text is needed outside QML.
	"""
	if level_label is None:
		level_label = "Lv." if abbreviated_tag else "Level"
	return f"{level_label}{level}"


def format_level_plus_one(level: int, *, abbreviated_tag: bool = True) -> str:
	"""IL: NumberFormat.FormatLevelPlusOne(int level, bool abbreviatedTag)"""
	return format_level(level + 1, abbreviated_tag=abbreviated_tag)


def format_percentage(value: float) -> str:
	"""IL: NumberFormat.FormatPercentage(F64/FD6 number)"""
	text = format_multiplier_3_significant_digits(value * 100.0)
	return f"{text}%"


def format_power(value: int | float) -> str:
	"""IL: NumberFormat.FormatPower(long/F64/FD6/UInt128)"""
	if value == 0:
		return ""
	text = format(float(value))
	return text if text else ""


def format_stat(value: float, digits: int = 0) -> str:
	"""IL: NumberFormat.FormatStat(F64/FD6 number, int digits = 0)"""
	if digits == 0:
		return format(value)
	return format_multiplier_1_significant_digits(value)
