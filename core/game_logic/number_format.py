from __future__ import annotations

import math


def format_stat(value: float, *, as_multiplier: bool = False) -> str:
	"""IL: NumberFormat.FormatStat(FD6/F64 value, asMultiplier)

	param_3 == 0 → Numbers.Format
	param_3 != 0 → Numbers.FormatMultiplier1SignificantDigits
	"""
	if as_multiplier:
		return _format_multiplier_one_significant_digit(value)
	return _format_number(value)


def _floor_to_significant(value: float, digits: int = 3) -> float:
	if value <= 0:
		return 0.0
	magnitude = int(math.floor(math.log10(value)))
	power = 10 ** (magnitude - digits + 1)
	return math.floor(value / power) * power


def _format_scaled_unit(scaled: float) -> str:
	if scaled >= 100:
		return str(int(scaled))
	if scaled >= 10:
		text = f"{scaled:.1f}".rstrip("0").rstrip(".")
		return text
	text = f"{scaled:.2f}".rstrip("0").rstrip(".")
	return text


_SCALED_SUFFIX_UNITS = (
	(1_000_000_000_000_000, 1_000_000_000_000_000, "Q"),
	(1_000_000_000_000, 1_000_000_000_000, "T"),
	(1_000_000_000, 1_000_000_000, "B"),
	(1_000_000, 1_000_000, "M"),
	(1_000, 1_000, "K"),
)


def _format_number(value: float) -> str:
	abs_value = abs(value)
	sign = "-" if value < 0 else ""

	if abs_value < 1_000:
		return f"{sign}{int(math.floor(abs_value))}"

	for threshold, divisor, suffix in _SCALED_SUFFIX_UNITS:
		if abs_value >= threshold:
			floored = _floor_to_significant(abs_value, 3)
			scaled = floored / divisor
			return f"{sign}{_format_scaled_unit(scaled)}{suffix}"

	return f"{sign}{int(math.floor(abs_value))}"


def _format_multiplier_one_significant_digit(value: float) -> str:
	scaled = round(value, 2)
	text = f"{scaled:.2f}".rstrip("0").rstrip(".")
	return text
