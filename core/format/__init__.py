"""Presentation formatting — IL ports outside Game.Logic (NumberFormat, StatsFormat, …)."""

from .format_currency import format_currency
from .localization import format_localized, get_translation
from .number_format import (
	format_currency_value,
	format_damage,
	format_drop_chance_percentage,
	format_level,
	format_level_plus_one,
	format_multiplier,
	format_percentage,
	format_power,
	format_stat,
)
from .numbers import (
	SUFFIXES,
	format as format_number,
	format_digits,
	format_long,
	format_multiplier_1_significant_digits,
	format_multiplier_3_significant_digits,
	format_multiplier_fixed,
	round_digits,
	round_down,
	round_up,
	truncate_to_two_decimals,
)

__all__ = [
	"SUFFIXES",
	"format_currency",
	"format_currency_value",
	"format_damage",
	"format_digits",
	"format_drop_chance_percentage",
	"format_level",
	"format_level_plus_one",
	"format_localized",
	"format_long",
	"format_multiplier",
	"format_multiplier_1_significant_digits",
	"format_multiplier_3_significant_digits",
	"format_multiplier_fixed",
	"format_number",
	"format_percentage",
	"format_power",
	"format_stat",
	"get_translation",
	"round_digits",
	"round_down",
	"round_up",
	"truncate_to_two_decimals",
]
