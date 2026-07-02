"""IL: TimeExtensions.Format(TimeSpan/MetaDuration, digits=2)."""
from __future__ import annotations

from config import string_literal

from . import numbers
from .localizer_base import get_localized

# IL StringLiteral_25726 — per-component "{number}{unit} " in TimeExtensions.Format
_TIMER_COMPONENT_FORMAT = string_literal(25726)

_DAYS_D_LOC_ID = "28308895591755776"
_HOURS_H_LOC_ID = "28308895591755777"
_MINUTES_M_LOC_ID = "28307134017630208"
_SECONDS_S_LOC_ID = "28307134051184640"


def _timer_units(language: str | None = None) -> tuple[str, str, str, str]:
	return (
		get_localized(_DAYS_D_LOC_ID, table="General", language=language) or "d",
		get_localized(_HOURS_H_LOC_ID, table="General", language=language) or "h",
		get_localized(_MINUTES_M_LOC_ID, table="General", language=language) or "m",
		get_localized(_SECONDS_S_LOC_ID, table="General", language=language) or "s",
	)


def format_timer_duration(
	seconds: int,
	language: str | None = None,
	*,
	digits: int | None = None,
	game_number_formatting_enabled: bool = True,
) -> str:
	"""IL: TimeExtensions.Format — up to `digits` largest non-zero d/h/m/s components."""
	if digits is None:
		digit_count = 2 if game_number_formatting_enabled else 4
	else:
		digit_count = digits
	if digit_count <= 0:
		return ""

	total_seconds = max(0, int(seconds))
	days = total_seconds // 86400
	remainder = total_seconds % 86400
	hours = remainder // 3600
	remainder %= 3600
	minutes = remainder // 60
	secs = remainder % 60

	day_unit, hour_unit, minute_unit, second_unit = _timer_units(language)
	parts: list[str] = []
	count = 0

	def _append(value: int, unit: str) -> None:
		parts.append(
			_TIMER_COMPONENT_FORMAT.format(numbers.format_long(value), unit)
		)

	if days >= 1:
		_append(days, day_unit)
		count += 1

	if hours > 0 and count < digit_count:
		_append(hours, hour_unit)
		count += 1

	if minutes > 0 and count < digit_count:
		_append(minutes, minute_unit)
		count += 1

	if secs >= 1 and count < digit_count:
		_append(secs, second_unit)

	text = "".join(parts)
	if len(text) > 1:
		return text[:-1]
	return text


def format_hatch_duration(seconds: int, language: str | None = None) -> str:
	return format_timer_duration(seconds, language)
