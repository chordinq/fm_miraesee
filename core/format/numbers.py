"""IL: Numbers (TypeDefIndex 7728) — suffix scaling, multipliers, rounding."""
from __future__ import annotations

import math
from collections.abc import Callable
from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING

from config import string_literal

if TYPE_CHECKING:
	pass

_SUFFIX_LITERAL_IDS: tuple[int, ...] = (
	22328, 22642, 20088, 24403, 23551, 2527, 3501, 3854, 5480, 6246, 7050, 7728,
	8249, 8567, 9817, 9923, 10020, 10405, 11232, 11802, 12193, 13053, 13080, 13739,
	15165, 17010, 17809, 18053, 18229, 18334, 18421, 2618, 2621, 2624, 2626, 2627,
	2628, 2629, 2630, 2631, 2633, 2634, 2635, 2636, 2637, 2640, 2641, 2650, 2651,
	2652, 2656, 2660, 2663, 2664, 2673, 2674, 2675, 3502, 3503, 3504, 3506, 3507,
	3509, 3510, 3511, 3512, 3515, 3516, 3517, 3520, 3522, 3523, 3525, 3526, 3527,
	3529, 3530, 3531, 3534, 3535, 3536, 3537, 3538,
)

SUFFIXES: tuple[str, ...] = tuple(
	string_literal(index) for index in _SUFFIX_LITERAL_IDS
)

_INT_FORMAT = string_literal(687)
_DOUBLE_FORMAT = string_literal(7728)


def round_down(value: float) -> int:
	"""IL: Numbers.RoundDown(double value)"""
	if not math.isfinite(value):
		return -2147483648
	return int(value)


def round_up(value: float) -> int:
	"""IL: Numbers.RoundUp(double value) — decompiled as ``(int)value``."""
	if not math.isfinite(value):
		return -2147483648
	return int(value)


def round_digits(value: float, digits: int) -> float:
	"""IL: Numbers.RoundDigits — Math.Round(..., MidpointRounding.ToEven)."""
	return round(value, digits)


def floor_double(value: float, digits: int) -> float:
	"""IL: Numbers.FloorDouble — Truncate(value × 10^(digits+1)) / 10^(digits+1)."""
	power = 10.0 ** (digits + 1)
	return math.trunc(power * value) / power


def ceil_double(value: float, digits: int) -> float:
	"""IL: Numbers.CeilDouble."""
	power = 10.0 ** digits
	return int(power * value) / power


def _log10_magnitude(value: float) -> int:
	if value <= 0.0 or not math.isfinite(value):
		return -2147483648
	log_value = math.log10(value)
	if log_value == math.inf:
		return -2147483648
	return int(log_value)


def _format_double_us(value: float) -> str:
	if value == int(value) and abs(value) < 1e15:
		return str(int(value))
	text = f"{value:.10f}".rstrip("0").rstrip(".")
	return text if text else "0"


def _string_without_trailing_zeroes(value: float, digits: int) -> str:
	"""IL: FormatMultiplier1SignificantDigits g__GetStringWithoutTrailingZeroes."""
	if digits <= 0:
		return str(int(math.trunc(value)))
	quantizer = Decimal(f"0.{'0' * (digits - 1)}1")
	rounded = Decimal(str(value)).quantize(quantizer, rounding=ROUND_HALF_UP)
	text = f"{rounded:f}"
	if "." not in text:
		return text
	return text.rstrip("0").rstrip(".")


def _format_with_suffix(
	value: float,
	*,
	significant_fn: Callable[[float], str],
) -> str:
	"""IL: g__FormatWithSuffix for 1- and 3-significant-digit multiplier paths."""
	sign = "-" if value < 0 else ""
	abs_value = abs(value)
	log_magnitude = _log10_magnitude(abs_value)
	if not math.isfinite(abs_value) or log_magnitude < 0:
		return sign + significant_fn(abs_value)
	suffix_index = log_magnitude // 3
	divisor = 10.0 ** (suffix_index * 3)
	unit = significant_fn(abs_value / divisor)
	if suffix_index < 1 or suffix_index > len(SUFFIXES):
		return sign + unit
	return sign + unit + SUFFIXES[suffix_index - 1]


def format_multiplier_1_significant_digits(value: float) -> str:
	"""IL: Numbers.FormatMultiplier1SignificantDigits(double value)"""
	if value >= 1000.0:
		return _format_with_suffix(
			value, significant_fn=format_multiplier_1_significant_digits
		)
	if value >= 100.0:
		floored = floor_double(value, 0)
		return _string_without_trailing_zeroes(floored, 0)
	floored = floor_double(value, 1)
	return _string_without_trailing_zeroes(floored, 1)


def format_multiplier_3_significant_digits(value: float) -> str:
	"""IL: Numbers.FormatMultiplier3SignificantDigits(double value)"""
	if value >= 1000.0:
		return _format_with_suffix(
			value, significant_fn=format_multiplier_3_significant_digits
		)
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


def _format_scaled_with_round(
	value: float,
	round_fn: Callable[[float], int],
) -> str:
	"""IL: Numbers.Format(double, round_fn, formatString) suffix branch."""
	abs_value = abs(value)
	sign = "-" if value < 0 else ""
	log_magnitude = _log10_magnitude(abs_value)
	if log_magnitude < 3:
		return f"{sign}{round_fn(abs_value)}"

	suffix_index = log_magnitude // 3
	divisor = 10.0 ** (suffix_index * 3)
	scale = 10.0 ** ((suffix_index * 3 - log_magnitude) + 2)
	rounded = round_fn((abs_value / divisor) * scale)
	display = rounded / scale
	if display >= 1000.0:
		display /= 1000.0
		suffix_index += 1

	if suffix_index < 1 or suffix_index > len(SUFFIXES):
		return f"{sign}{round_fn(abs_value)}"

	text = _format_double_us(display)
	return f"{sign}{text}{SUFFIXES[suffix_index - 1]}"


def format(
	value: float,
	round_fn: Callable[[float], int] | None = None,
	show_below_one: bool = False,
) -> str:
	"""IL: Numbers.Format overloads."""
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


def format_digits(value: float) -> str:
	"""IL: Numbers.FormatDigits — Format(value, RoundUp, showBelowOne: true)."""
	return format(value, round_up, show_below_one=True)


def format_long(number: int) -> str:
	"""IL: Numbers.FormatLong(long number)"""
	return format(float(number))


def format_multiplier(value: float, digits: int = 2) -> str:
	"""IL: Numbers.FormatMultiplier(double value, int digits)"""
	if value > 1000.0:
		return format(value, round_down)
	rounded = round_digits(value, digits)
	return _format_double_us(rounded)


def format_multiplier_fixed(
	value: float,
	digits: int = 2,
	rounding_mode: object | None = None,
) -> str:
	"""IL: Numbers.FormatMultiplierFixed(double value, int digits, RoundingMode?)"""
	del rounding_mode
	if digits <= 0:
		rounded = round_digits(value, 0)
		return str(int(rounded))
	rounded = round_digits(value, digits)
	text = f"{rounded:.{digits}f}".rstrip("0").rstrip(".")
	return text if text else "0"


def truncate_to_two_decimals(number: float) -> str:
	"""IL: Numbers.TruncateToTwoDecimals(double number)"""
	truncated = math.trunc(number * 100.0) / 100.0
	return _format_double_us(truncated)
